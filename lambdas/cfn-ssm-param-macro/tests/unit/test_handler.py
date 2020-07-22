import json
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

import boto3
from botocore.stub import Stubber
from ssm_param import app


class TestHandler(unittest.TestCase):


  def create_mock_response(self, param_type, param_value):
    return {
      'Parameter': {
        'Name': 'test-param',
        'Type': param_type,
        'Value': param_value,
        'Version': 1,
        'LastModifiedDate': '2020-01-15 10:35:06.976938',
        'ARN': 'arn:aws:ssm:us-east-1:123456789abc:parameter/test-param'},
        'ResponseMetadata': {
          'RequestId': '239250d2-b312-474f-9009-303ca4c2fac0',
          'HTTPStatusCode': 200,
          'HTTPHeaders': {
            'x-amzn-requestid': '239250d2-b312-474f-9009-303ca4c2fac0',
            'content-type': 'application/x-amz-json-1.1',
            'content-length': '239',
            'date': 'Wed, 15 Jan 2020 18:26:27 GMT'
          },
          'RetryAttempts': 0
        }
      }


  # happy path
  def test_string(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber:
      expected_value = 'first test string'
      response = self.create_mock_response('String', expected_value)
      stubber.add_response('get_parameter', response)
      app.get_ssm_client = MagicMock(return_value=ssm)

      with open(r'tests/events/string.json') as file:
        event = json.load(file)
      self.event = event
      result = app.handler(self.event, None)
      print(result)
      fragment = result['fragment']
      print(fragment)

      self.assertEqual(fragment, expected_value)


  # expect failure if Type is missing
  def test_type_missing(self):
    with open(r'tests/events/type_param_missing.json') as file:
      event = json.load(file)
    self.event = event
    result = app.handler(self.event, None)
    self.assertEqual('failure', result['status'])
    self.assertEqual(
      app.MISSING_TYPE_ERROR_MESSAGE,
      result['errorMessage'])


  # expect failure if Type is invalid
  def test_invalid_type(self):
    with open(r'tests/events/invalid_type.json') as file:
      event = json.load(file)
    self.event = event
    result = app.handler(self.event, None)
    self.assertEqual('failure', result['status'])
    self.assertEqual(
      app.MISSING_TYPE_ERROR_MESSAGE,
      result['errorMessage'])


  # expect failure if Name is missing
  def test_name_missing(self):
    with open(r'tests/events/name_param_missing.json') as file:
      event = json.load(file)
    self.event = event
    result = app.handler(self.event, None)
    self.assertEqual('failure', result['status'])
    self.assertEqual(
      app.MISSING_NAME_ERROR_MESSAGE,
      result['errorMessage'])


  # expect failure if an invalid name is used
  def test_invalid_name(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber:
      stubber.add_client_error(
        method='get_parameter',
        service_error_code='ParameterNotFound')
      app.get_ssm_client = MagicMock(return_value=ssm)
      with open(r'tests/events/invalid_name.json') as file:
        self.event = json.load(file)
      result = app.handler(self.event, None)
      print(result)
      self.assertEqual('failure', result['status'])
      param_not_found_error = 'An error occurred (ParameterNotFound) when calling the GetParameter operation: '
      self.assertEqual(
        param_not_found_error,
        result['errorMessage'])
