import json
import unittest
from unittest.mock import patch

import botocore
from ssm_param import app


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
      return self.response
    else:
      raise ValueError(f'Mock api call fail. Expected operation GetParameter, got {operation_name}')


  # happy path
  def test_string(self):
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
      with open(r'tests/events/string.json') as file:
        event = json.load(file)
      self.event = event
      result = app.handler(self.event, None)
      fragment = result["fragment"]
      print(fragment)

      self.assertEqual(fragment, expected_value)


  # expect failure if Type is missing
  def test_type_missing(self):
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
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
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
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
    with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
      expected_value = 'first test string'
      self.create_mock_response('String', expected_value)
      with open(r'tests/events/name_param_missing.json') as file:
        event = json.load(file)
      self.event = event
      result = app.handler(self.event, None)
      self.assertEqual('failure', result['status'])
      self.assertEqual(
        app.MISSING_NAME_ERROR_MESSAGE,
        result['errorMessage'])
