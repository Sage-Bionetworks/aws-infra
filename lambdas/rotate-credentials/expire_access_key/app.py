# Lambda script to setup a IAM user access key rotation schedule.
# This script is not designed to actually auto rotate keys. It's
# designed to make the IAM user rotate their own keys because
# there is no mechanism to auto rotate keys on behalf of another user
# in AWS.
#
# This scrip does two things:
# 1. Notify users when their key is about to expire and ask them to
#    rotate their key themselves.
# 2. Upon key expiration it will automatically deactivate keys and
#    notify users that they will need to rotate their expired keys.
#
# This is designed to review only IAM users with AWS console
# access (human users).  It will skip all other user accounts.
# The purpose is to avoid expiring access keys for service accounts.
#
# Notifications:
#
#   Email user when:
#     1. Their key has expired and been deactivated
#     2. Their key has expired but not deactivated
#     3. Their key is close to expiring (or in a configurable expiration grace period)
#
#   SNS topic:
#     It can be configured to send expired key reports to an SNS topic.
from __future__ import print_function
import logging
import os
import csv
import json
import re
from time import sleep
import dateutil.parser
from datetime import datetime, timedelta, date

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.debug("Received event: " + json.dumps(event, sort_keys=True))

    # These should be passed in via Lambda Environment Variables
    try:
        DISABLE_KEYS = True if os.environ['DISABLE_KEYS'].lower() == 'true' else False
        SEND_REPORT = True if os.environ['SEND_REPORT'].lower() == 'true' else False
        SEND_EMAIL = True if os.environ['SEND_EMAIL'].lower() == 'true' else False
        SENDER_EMAIL = os.environ['SENDER_EMAIL']
        REPORT_TOPIC_ARN = os.environ['REPORT_TOPIC_ARN']
        GRACE_PERIOD = int(os.environ['GRACE_PERIOD'])
        MAX_ACCESS_KEY_AGE = int(os.environ['MAX_ACCESS_KEY_AGE'])
    except (KeyError, ValueError, Exception) as e:
        logger.error(e.response['Error']['Message'])

    # notification messages
    user_message_deactivated_key = '\n\tYour access key {} has been deactivated, please rotate your key.'
    user_message_expired_key = '\n\tYour access key {} has expired, please rotate your key.'
    user_message_expiring_key = '\n\tYour access key {} will expire in {} days, please rotate your key.'
    report_message_deactivated_key = '\n\tAccess key {} for user {} has been deactivated.'
    report_message_expired_key = '\n\tAccess key {} for user {} has expired.'

    max_age = MAX_ACCESS_KEY_AGE  # access key expiration setting
    try:
        credential_report = get_credential_report()

        aws_account_identity = get_aws_account_identity()  # either account name or id
        logger.debug('aws_account_identity: {}'.format(aws_account_identity))

        report = ''     # a report summary for account admins
        # Iterate over the credential report, use the report to determine the expiration date
        # Then query for access keys, and use the key creation data to determine key expiration
        iam_client = boto3.client('iam')
        for row in credential_report:
            logger.debug('processing iam account: ' + row['user'])
            # Skip IAM Users without passwords (service accounts), root user should not have access keys
            if row['password_enabled'] != "true": continue
            user_notice = ''     # notices for the IAM users
            try:
                # IAM client will fail if root user contains active keys because list_access_keys
                # method will fail for root username '<root_account>'
                iam_response = iam_client.list_access_keys(UserName=row['user'])
                logger.debug("list_access_key iam_response: " + json.dumps(iam_response, default = obj_converter))
                for key in iam_response['AccessKeyMetadata'] :
                    logger.debug('processing access key: ' + key['AccessKeyId'])
                    if key['Status'] == "Inactive" : continue
                    days_till_expire = get_days_until_key_expires(key['CreateDate'], max_age)
                    logger.debug('days_till_expire: ' + str(days_till_expire))
                    if days_till_expire <= 0:  # key has expired
                        logger.debug('access key {}:{}:{} has expired'.
                                     format(aws_account_identity, row['user'], key['AccessKeyId']))
                        if DISABLE_KEYS:
                            disable_key(key['AccessKeyId'], row['user'])
                            logger.debug('deactivated access key {}:{}:{}'.
                                         format(aws_account_identity, row['user'], key['AccessKeyId']))
                            user_notice = user_notice + user_message_deactivated_key.format(key['AccessKeyId'])
                            report = report + report_message_deactivated_key.format(key['AccessKeyId'], row['user'])

                        else:
                            logger.debug('expired access key {}:{}:{}'.
                                         format(aws_account_identity, row['user'], key['AccessKeyId']))
                            user_notice = user_notice + user_message_expired_key.format(key['AccessKeyId'])
                            report = report + report_message_expired_key.format(key['AccessKeyId'], row['user'])

                    elif days_till_expire < GRACE_PERIOD:
                        logger.debug('expiring access key {}:{}:{}'.
                                     format(aws_account_identity, row['user'], key['AccessKeyId']))
                        user_notice = user_notice + user_message_expiring_key.format(key['AccessKeyId'],
                                                                                     days_till_expire)

            except ClientError as e:
                logger.error(e.response['Error']['Message'])

            if user_notice != '' and SEND_EMAIL and isValidEmail(row['user']):     # email to iam users
                logger.info("Emailing user " + row['user'])
                subject = "Notification from AWS account {}".format(aws_account_identity)
                footer = '\n\tAWS account policy requires rotating access keys every {} days.'.format(max_age)
                body = user_notice + footer
                email_user(SENDER_EMAIL, row['user'], subject, body)

        if report != '' and SEND_REPORT:      # send reports to an SNS topic
            logger.info("Publishing report to " + REPORT_TOPIC_ARN)
            publish_sns_topic(REPORT_TOPIC_ARN,
                              "Notification from AWS account {}".format(aws_account_identity),
                              report)
        return response({'message': 'Success'}, 200)
    except Exception as e:
        return response({'message': e.message}, 400)

def response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }

# format objects to strings (for debugging only)
def obj_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

# simple lenient check for valid email format (requires * and . in the string)
def isValidEmail(email):
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
        return True
    return False

# get account identity info for reporting
def get_aws_account_identity():
    iam_client = boto3.client('iam')
    try:
        account_aliases = iam_client.list_account_aliases()['AccountAliases']
        if account_aliases:
            account_identity = account_aliases[0]
        else:
            logger.info("AWS account name is not set, use account id instead")
            sts_client = boto3.client('sts')
            account_identity = sts_client.get_caller_identity()['Account']
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

    return str(account_identity)

# publish notifications to an SNS topic
def publish_sns_topic(topic_arn, subject, message):
    client = boto3.client('sns')
    try:
        response = client.publish(TopicArn=topic_arn, Subject=subject, Message=message)
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

# Send notification to IAM users
def email_user(sender, recipient, subject, body):

        client = boto3.client('ses')

        # This address must be verified with Amazon SES.
        SENDER = sender

        # if SES is still in the sandbox, this address must be verified.
        RECIPIENT = recipient

        # Specify a configuration set. If you do not want to use a configuration
        # set, comment the following variable, and the
        # ConfigurationSetName=CONFIGURATION_SET argument below.
        # CONFIGURATION_SET = "ConfigSet"

        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        # AWS_REGION = "us-west-2"

        # The subject line for the email.
        SUBJECT_TEXT = subject

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = body

        # The HTML body of the email.
        BODY_HTML1 = """<html>
        <head></head>
        <body>
          <p>"""
        BODY_HTML2 = """</p>
        </body>
        </html>
        """

        # The character encoding for the email.
        CHARSET = "UTF-8"

        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML1 + BODY_TEXT + BODY_HTML2,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT_TEXT,
                    },
                },
                Source=SENDER,
                # If you are not using a configuration set, comment or delete the
                # following line
                # ConfigurationSetName=CONFIGURATION_SET,
            )
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
        else:
            logger.info("Email sent to " + RECIPIENT)
            logger.info("Message ID: " + response['MessageId'])


# Get the AWS account's credential report (in CSV) and return a list of credentials info
def get_credential_report():

    # initial request to generate report will respond with status='STARTED' and may
    # take a few seconds to finish, keep requesting until the status is 'COMPLETE'
    iam_client = boto3.client('iam')
    resp1 = iam_client.generate_credential_report()

    if resp1['State'] == 'COMPLETE':
        try:
            response = iam_client.get_credential_report()
            credential_report_csv = response['Content']
            reader = csv.DictReader(credential_report_csv.splitlines())
            credential_report = []
            for row in reader:
                credential_report.append(row)
            return(credential_report)
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
    else:
        # Request again until AWS finishes generating the report
        sleep(2)
        return get_credential_report()


# Get the number of days until an access key is expired
# days <= 0 means key has expired
def get_days_until_key_expires(last_changed, max_age):
    # Ok - So last_changed can either be a string to parse or already a datetime object.
    # Handle these accordingly
    try:
        if type(last_changed) is str:
            last_changed_date=dateutil.parser.parse(last_changed).date()
        elif type(last_changed) is datetime:
            last_changed_date=last_changed.date()
        else:
            raise ValueError

        expires = (last_changed_date + timedelta(max_age)) - date.today()
    except ValueError as e:
        logger.error(e.response['Error']['Message'])

    return expires.days


# disable an access key
def disable_key(AccessKeyId, UserName):
    iam_client = boto3.client('iam')
    try:
        response = iam_client.update_access_key(UserName=UserName,
                                                AccessKeyId=AccessKeyId,
                                                Status='Inactive')
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

if __name__ == "__main__":
    lambda_handler("event","context")
