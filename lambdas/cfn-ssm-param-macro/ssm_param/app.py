import json
import traceback

import boto3
from botocore.exceptions import ClientError

SSM_PARAM_TYPES = ['String', 'SecureString', 'StringList']
MISSING_TYPE_ERROR_MESSAGE = f""""Type" parameter, the type of key in the SSM
parameter store, is required, and must be one of {SSM_PARAM_TYPES}"""
MISSING_NAME_ERROR_MESSAGE = """"Name" parameter (name of key in SSM parameter
store) is required"""


def get_ssm_client():
  return boto3.client('ssm')


def handle_transform(parameters):
    if 'Type' not in parameters or parameters['Type'] not in SSM_PARAM_TYPES:
      raise ValueError(MISSING_TYPE_ERROR_MESSAGE)
    if 'Name' not in parameters:
      raise ValueError(MISSING_NAME_ERROR_MESSAGE)

    decrypt = True if parameters['Type'] == SSM_PARAM_TYPES[1] else False

    client = get_ssm_client()

    try:
      response = client.get_parameter(
        Name=parameters['Name'],
        WithDecryption=decrypt)
      fragment = response['Parameter']['Value']
      return fragment
    except ClientError as e:

      raise e


def handler(event, context):
    status = 'success'
    response = {
      'requestId': event['requestId'],
      'status': 'success'
    }

    try:
      response['fragment'] = handle_transform(event['params'])
    except Exception as e:
      traceback.print_exc()
      response['status'] = 'failure'
      response['errorMessage'] = str(e)

    return response
