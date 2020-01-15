import boto3
import json
import traceback

def handle_transform(parameters):
    secure = False
    if 'Secure' in parameters and parameters['Secure'] is True:
        secure = True
    if 'SsmKeyName' not in parameters:
        raise ValueError('"SsmKeyName" parameter is required')
    keyname = parameters['SsmKeyName']
    client = boto3.client('ssm')
    response = client.get_parameter(
        Name=keyname,
        WithDecryption=secure)
    print(response)
    fragment = response['Parameter']['Value']
    return fragment


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
