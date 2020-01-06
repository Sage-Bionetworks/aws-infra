import json
import traceback


def handle_transform(parameters):
  operation = parameters['Operation']
  transform_string = parameters['TransformString']
  fragment = []
  input_list = parameters['List']
  prepend = parameters['Prepend']
  if prepend:
    fragment = [transform_string + item for item in input_list]
  else:
    fragment = [item + transform_string for item in input_list]
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
