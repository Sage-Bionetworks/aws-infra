import unittest
from ssm_param.app import handler
from unittest.mock import patch
import botocore
import json


class test_handler(unittest.TestCase):


  def create_mock_response(self, param_type, param_value):
    self.response = {
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


  def mock_make_api_call(self, operation_name, kwarg):
    if operation_name == 'GetParameter':
      print(kwarg)
      return self.response
    else:
      raise ValueError(f'Mock api call fail. Expected operation GetParameter, got {operation_name}')

  # happy path
  def test_string(self):
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
      with open(r'tests/events/happy.json') as file:
        event = json.load(file)
      self.event = event
      result = handler(self.event, None)
      fragment = result["fragment"]
      print(fragment)

      self.assertEqual(fragment, expected_value)


  # test that this will still work if secure param is left off as it has a default value
  def test_secure_param_missing(self):
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
      with open(r'tests/events/secure_param_missing.json') as file:
        event = json.load(file)
      self.event = event
      result = handler(self.event, None)
      fragment = result["fragment"]
      print(fragment)

      self.assertEqual(fragment, expected_value)


  # expect failure if keyname is missing
  def test_keyname_missing(self):
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
      with open(r'tests/events/keyname_missing.json') as file:
        event = json.load(file)
      self.event = event
      result = handler(self.event, None)
      self.assertEqual('failure', result['status'])
      self.assertEqual(
        '"SsmKeyName" parameter is required',
        result['errorMessage']
      )
