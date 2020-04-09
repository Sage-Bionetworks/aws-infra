import boto3
import json
import logging

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
    name = event['ResourceProperties']['Name']
    ssm_doc_name = event['ResourceProperties']['SsmDocName']
    ssm_doc_version = event['ResourceProperties']['SsmDocVersion']
    assume_role = event['ResourceProperties']['AssumeRole']
    return aws_account_id, name, ssm_doc_name, ssm_doc_version, assume_role

def validate_parameters(aws_account_id, name, ssm_doc_name, ssm_doc_version, assume_role):
    logger.debug("Validate SSM doc " + ssm_doc_name + ", " + ssm_doc_version)
    ssm = boto3.client("ssm")
    ssm.get_document(
        Name=ssm_doc_name,
        DocumentVersion=ssm_doc_version,
    )

    assume_role_name = assume_role.split(':')[5].split('/')[1]
    logger.debug("Validate role: " + assume_role_name)
    iam = boto3.client("iam")
    iam.get_role(
        RoleName=assume_role_name
    )

def create_provider(aws_account_id, name, ssm_doc_name, ssm_doc_version, assume_role):
    response = sc.create_service_action(
        Name=name,
        DefinitionType='SSM_AUTOMATION',
        Definition= {
                "Name": ssm_doc_name,
                "Version": ssm_doc_version,
                "AssumeRole": assume_role,
                "Parameters": "[{\"Name\":\"AutomationAssumeRole\",\"Type\":\"TARGET\"}]"
              }
    )
    id = response['ServiceActionDetail']['ServiceActionSummary']['Id']
    logger.info("created sc action " + id)
    return id

@helper.create
def create(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    validate_parameters(*get_parameters(event))
    return create_provider(*get_parameters(event))

@helper.delete
def delete(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    id = event['PhysicalResourceId']
    logger.info("deleting sc action " + id)
    sc.delete_service_action(
        Id=id
    )

@helper.update
def update(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    new_properties = event['ResourceProperties']
    old_properties = event['OldResourceProperties']
    id = event['PhysicalResourceId']
    if new_properties != old_properties:
        response = sc.update_service_action(
            Id=id,
            Name=new_properties['Name'],
            Definition= {
                    "Name": new_properties['SsmDocName'],
                    "Version": new_properties['SsmDocVersion'],
                    "AssumeRole": new_properties['AssumeRole'],
                    "Parameters": "[{\"Name\":\"AutomationAssumeRole\",\"Type\":\"TARGET\"}]"
                  }
        )
        id = response['ServiceActionDetail']['ServiceActionSummary']['Id']
        logger.info("updated sc action = " + id)
    return id

def lambda_handler(event, context):
    helper(event, context)
