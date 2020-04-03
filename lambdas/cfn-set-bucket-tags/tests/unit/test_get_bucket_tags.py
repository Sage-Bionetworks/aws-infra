import unittest
from unittest.mock import MagicMock

import boto3
import botocore
from botocore.stub import Stubber

from set_bucket_tags import app


class TestGetBucketTags(unittest.TestCase):

  def test_valid_bucket(self):
    s3 = boto3.client('s3')
    with Stubber(s3) as stubber:
      tags = [
        {'Key': 'heresatag', 'Value': 'heresatagvalue'},
        {'Key': 'theresatag', 'Value': 'theresatagvalue'}
      ]
      response = {
        'ResponseMetadata': {'RequestId': 'gobbledygoop','HTTPStatusCode': 200,},
        'TagSet': tags
      }
      stubber.add_response('get_bucket_tagging', response)
      app.get_s3_client = MagicMock(return_value=s3)
      valid_bucket_name ='some_reasonable_bucket_name'
      result = app.get_bucket_tags(valid_bucket_name)
      self.assertEqual(tags, result)


  def test_invalid_bucket(self):
    s3 = boto3.client('s3')
    with Stubber(s3) as stubber, self.assertRaises(botocore.exceptions.ClientError):
      stubber.add_client_error(
        method='get_bucket_tagging',
        service_error_code='NoSuchBucket',
        service_message='The specified bucket does not exist',
        http_status_code=404)
      app.get_s3_client = MagicMock(return_value=s3)
      invalid_bucket_name ='some_unreasonable_bucket_name'
      result = app.get_bucket_tags(invalid_bucket_name)


  def test_no_tags(self):
    s3 = boto3.client('s3')
    with Stubber(s3) as stubber, self.assertRaises(Exception):
      response = {
        'ResponseMetadata': {'RequestId': 'gobbledygoop','HTTPStatusCode': 200,},
        'TagSet': []
      }
      stubber.add_response('get_bucket_tagging', response)
      app.get_s3_client = MagicMock(return_value=s3)
      valid_bucket_name ='some_reasonable_bucket_name'
      result = app.get_bucket_tags(valid_bucket_name)
