import json
import unittest
from unittest.mock import MagicMock, patch

import boto3
import botocore
from botocore.stub import Stubber

from set_bucket_tags import app


class TestHandler(unittest.TestCase):

  # happy path
  def test_adding_tags(self):
    with open(r'tests/events/event.json') as file:
      event = json.load(file)
    s3 = boto3.client('s3')
    with Stubber(s3) as stubber, \
      patch('set_bucket_tags.app.get_bucket_name') as name_mock, \
      patch('set_bucket_tags.app.get_bucket_tags') as get_mock, \
      patch('set_bucket_tags.app.get_principal_arn') as arn_mock, \
      patch('set_bucket_tags.app.get_synapse_user_name') as syn_mock, \
      patch('set_bucket_tags.app.add_owner_email_tag') as tags_mock:
        name_mock.return_value = 'some-improbable-bucket-name'
        tags_mock.return_value = [{ 'Key': 'OwnerEmail', 'Value': 'janedoe@synapse.org' }]
        stubber.add_response(
          method='put_bucket_tagging',
          service_response={
            'ResponseMetadata': {
              'RequestId': '12345',
              'HostId': 'etc',
              'HTTPStatusCode': 204,
              'HTTPHeaders': {}
            }})
        app.get_s3_client = MagicMock(return_value=s3)
        result = app.handler(event, None)
    self.assertEqual('success', result['status'])


  def test_missing_bucket_name(self):
    with open(r'tests/events/param_missing.json') as file:
      event = json.load(file)
    result = app.handler(event, None)
    self.assertEqual('failure', result['status'])
    self.assertEqual(
      app.MISSING_BUCKET_NAME_ERROR_MESSAGE,
      result['errorMessage'])
