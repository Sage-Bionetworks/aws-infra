import boto3
import json
import logging

from crhelper import CfnResource
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
helper = CfnResource(
    json_logging=False, log_level='INFO', boto_level='CRITICAL')

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

def create_provider(aws_account_id, service_action_id, product_id, provisioning_artifact_id):
    try:
        response = sc.batch_associate_service_action_with_provisioning_artifact(
            ServiceActionAssociations=[
                {
                    'ServiceActionId': service_action_id,
                    'ProductId': product_id,
                    'ProvisioningArtifactId': provisioning_artifact_id
                },
            ],
        )
    except ClientError as e:
        raise e

@helper.create
def create(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    return create_provider(*get_parameters(event))


@helper.delete
def delete(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    disassociate_action(*get_parameters(event))


def disassociate_action(aws_account_id, service_action_id, product_id, provisioning_artifact_id):
    try:
        response = sc.batch_disassociate_service_action_from_provisioning_artifact(
            ServiceActionAssociations=[
                {
                    'ServiceActionId': service_action_id,
                    'ProductId': product_id,
                    'ProvisioningArtifactId': provisioning_artifact_id
                },
            ],
        )
    except ClientError as e:
        raise e

@helper.update
def update(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    reassociate_action(event)

def reassociate_action(event):
    # remove association with existing project (or version) then add association with new project (or version)
    try:
        new_properties = event['ResourceProperties']
        old_properties = event['OldResourceProperties']
        if new_properties != old_properties:
            logger.info("removing association " + old_properties['ServiceActionId'])
            remove_response = sc.batch_disassociate_service_action_from_provisioning_artifact(
                ServiceActionAssociations=[
                    {
                        'ServiceActionId': old_properties['ServiceActionId'],
                        'ProductId': old_properties['ProductId'],
                        'ProvisioningArtifactId': old_properties['ProvisioningArtifactId']
                    },
                ],
            )

            logger.info("adding association " + new_properties['ServiceActionId'])
            add_response = sc.batch_associate_service_action_with_provisioning_artifact(
                ServiceActionAssociations=[
                    {
                        'ServiceActionId': new_properties['ServiceActionId'],
                        'ProductId': new_properties['ProductId'],
                        'ProvisioningArtifactId': new_properties['ProvisioningArtifactId']
                    },
                ],
            )
    except ClientError as e:
        raise e

def lambda_handler(event, context):
    helper(event, context)
