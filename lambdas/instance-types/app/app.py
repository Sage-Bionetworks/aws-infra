#! /usr/bin/env python3.7

import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

instance_type_filters = [
  {
    'Name': 'current-generation',
    'Values': [
        'true',
    ]
  },
  {
    'Name': 'bare-metal',
    'Values': [
        'false',
    ]
  }
]

# removes the current classes of high memory, accelerated computing,
# and storage optimized instances
restricted_prefixes = [
  'x1', 'z1', 'p3', 'p2', 'inf1', 'g4', 'g3', 'f1', 'i3', 'd2', 'h1'
]

def instance_type_is_valid(it):
  for prefix in restricted_prefixes:
    if it.startswith(prefix):
      return False
  return True


def get_instance_types():
  ec2 = boto3.client('ec2')

  results = []
  next_token = ''
  # This is necessary because a paginator cannot be used with
  # command describe_instance_types
  while next_token is not False:
    if next_token:
      response = ec2.describe_instance_types(
        Filters=instance_type_filters,
        NextToken=next_token
      )
    else:
      response = ec2.describe_instance_types(
        Filters=instance_type_filters
      )
    results = results + response['InstanceTypes']
    if 'NextToken' in response:
      next_token = response['NextToken']
    else:
      next_token = False

  return sorted([result['InstanceType'] for result in results])


def filter_types(instance_types):
  return [
    instance_type
    for instance_type in instance_types
    if instance_type_is_valid(instance_type)
  ]


def format_types(instance_types):
  return '\n'.join(
    [
      f'- {instance_type}'
      for instance_type in instance_types
    ]
  )


def write_to_S3(yaml):
  encoded = yaml.encode('utf-8')

  #bucket_name = 'essentials-awss3lambdaartifactsbucket-x29ftznj6pqw'
  bucket_name = os.environ['OUTPUT_BUCKET']
  file_name = 'instance-types.yaml'
  s3_path = file_name

  s3 = boto3.resource('s3')
  s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded)


def lambda_handler(event, context):
  logger.debug('Received event: ' + json.dumps(event, sort_keys=True))

  instance_types = get_instance_types()

  valid_types = filter_types(instance_types)

  yaml = format_types(valid_types)

  write_to_S3(yaml)
