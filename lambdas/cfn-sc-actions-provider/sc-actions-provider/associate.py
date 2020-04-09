import boto3
import json
import logging
import requests

from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(
    json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

try:
    sc = boto3.client("servicecatalog")
except Exception as e:
    helper.init_failure(e)

def get_parameters(event):
    aws_account_id = event['StackId'].split(':')[4]
    service_action_id = event['ResourceProperties']['ServiceActionId']
    product_id = event['ResourceProperties']['ProductId']
    provisioning_artifact_id = event['ResourceProperties']['ProvisioningArtifactId']
    return aws_account_id, service_action_id, product_id, provisioning_artifact_id

def validate_parameters(aws_account_id, service_action_id, product_id, provisioning_artifact_id):
    sc.describe_provisioning_artifact(
        ProductId=product_id,
        ProvisioningArtifactId=provisioning_artifact_id
    )

def create_provider(aws_account_id, service_action_id, product_id, provisioning_artifact_id):

    logger.debug(
        "Associate action " + service_action_id + " with product " + product_id + ", " + provisioning_artifact_id)
    response = sc.associate_service_action_with_provisioning_artifact(
        ProductId=product_id,
        ServiceActionId=service_action_id,
        ProvisioningArtifactId=provisioning_artifact_id
    )

@helper.create
def create(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    validate_parameters(*get_parameters(event))
    if create_provider(*get_parameters(event)):
        return True
    else:
        logger.debug("Send cloudformation a FAILED response")
        status = 'FAILED'
        reason = "Failed to create a sevice catalog association"
        data = {}
        send_response(event, context, status, reason, data)
        return False

@helper.delete
def delete(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    disassociate_action(*get_parameters(event))

def disassociate_action(aws_account_id, service_action_id, product_id, provisioning_artifact_id):
    response = sc.disassociate_service_action_from_provisioning_artifact(
        ServiceActionAssociations=[
            {
                'ServiceActionId': service_action_id,
                'ProductId': product_id,
                'ProvisioningArtifactId': provisioning_artifact_id
            },
        ],
    )

@helper.update
def update(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    reassociate_action(event)

def reassociate_action(event):
    # remove association with existing project (or version) then add association with new project (or version)
    new_properties = event['ResourceProperties']
    old_properties = event['OldResourceProperties']
    if new_properties != old_properties:
        logger.info("removing association " + old_properties['ServiceActionId'])
        remove_response = sc.disassociate_service_action_from_provisioning_artifact(
            ServiceActionAssociations=[
                {
                    'ServiceActionId': old_properties['ServiceActionId'],
                    'ProductId': old_properties['ProductId'],
                    'ProvisioningArtifactId': old_properties['ProvisioningArtifactId']
                },
            ],
        )

        logger.info("adding association " + new_properties['ServiceActionId'])
        add_response = sc.associate_service_action_with_provisioning_artifact(
            ServiceActionAssociations=[
                {
                    'ServiceActionId': new_properties['ServiceActionId'],
                    'ProductId': new_properties['ProductId'],
                    'ProvisioningArtifactId': new_properties['ProvisioningArtifactId']
                },
            ],
        )

def send_response(event, context, status, reason, data):
    responseBody = {'Status': status,
                    'Reason': reason,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': data}
    logger.debug('RESPONSE BODY:n' + json.dumps(responseBody))
    try:
        req = requests.put(event['ResponseURL'], data=json.dumps(responseBody))
        if req.status_code != 200:
            logger.debug(req.text)
            raise Exception('Recieved non 200 response while sending response to CFN.')
        return
    except requests.exceptions.RequestException as e:
        raise

def lambda_handler(event, context):
    helper(event, context)
