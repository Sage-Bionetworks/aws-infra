import boto3
import json
import logging

from crhelper import CfnResource
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
helper = CfnResource(
    json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

try:
    sc = boto3.client("servicecatalog")
except Exception as e:
    helper.init_failure(e)

def get_parameters(event):
    aws_account_id = event['StackId'].split(':')[4]
    name = event['ResourceProperties']['Name']
    version = event['ResourceProperties']['Version']
    assume_role = event['ResourceProperties']['AssumeRole']
    return aws_account_id, name, version, assume_role

def create_provider(aws_account_id, name, version, assume_role):
    try:
        response = sc.create_service_action(
            Name=name,
            DefinitionType='SSM_AUTOMATION',
            Definition= {
                    "Name": name,
                    "Version": version,
                    "AssumeRole": assume_role,
                    "Parameters": "[{\"Name\":\"AutomationAssumeRole\",\"Type\":\"TARGET\"}]"
                  }
        )
        resource_id = response['ServiceActionDetail']['ServiceActionSummary']['Id']
        logger.info("resource_id = " + resource_id)
        return resource_id
    except ClientError as e:
        raise e

@helper.create
def create(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    return create_provider(*get_parameters(event))

@helper.delete
def delete(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    try:
        id = event['PhysicalResourceId']
        logger.info("resource id = " + id)
        sc.delete_service_action(
            Id=id
        )
    except ClientError as e:
        raise e

def lambda_handler(event, context):
    helper(event, context)
