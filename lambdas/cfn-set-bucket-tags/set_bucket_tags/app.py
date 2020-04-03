import logging
import traceback

import boto3
import requests


MISSING_BUCKET_NAME_ERROR_MESSAGE = 'BucketName parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_s3_client():
  return boto3.client('s3')


def get_bucket_name(event):
  parameters = event['params']
  bucket_name = parameters.get('BucketName')
  if not bucket_name:
    raise ValueError(MISSING_BUCKET_NAME_ERROR_MESSAGE)
  return bucket_name


def get_bucket_tags(bucket_name):
  client = get_s3_client()
  log.info(f'Get tags for bucket named {bucket_name}')
  response = client.get_bucket_tagging(Bucket=bucket_name)
  log.debug(f'Tags response: {response}')
  tags = response.get('TagSet')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')
  return tags


def get_principal_arn(tags):
  principal_arn_tag = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == principal_arn_tag:
      principal_arn_value = tag.get('Value')
      return principal_arn_value
  else:
    raise ValueError('Could not derive a provisioningPrincipalArn from tags')


def get_synapse_user_name(principal_arn):
  synapse_id = principal_arn.split('/')[-1]
  if not synapse_id.isdigit():
    error_msg = (f'The synapse_id {synapse_id} derived from the principal_arn'
      f'{principal_arn} is in an unexpected format')
    raise ValueError(error_msg)
  synapse_url = f'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/{synapse_id}'
  response = requests.get(synapse_url)
  response.raise_for_status()
  user_profile = response.json()
  user_name = user_profile.get('userName')
  return user_name


def add_owner_email_tag(tags, synapse_username):
  synapse_email = f'{synapse_username}@synapse.org'
  owner_email_tag = { 'Key': 'OwnerEmail', 'Value': synapse_email}
  tags.append(owner_email_tag)
  return tags


def handler(event, context):
  log.info('Start SetBucketTags Lambda processing')
  response = {
    'requestId': event['requestId'],
    'status': 'success'
  }

  try:
    bucket_name = get_bucket_name(event)
    tags = get_bucket_tags(bucket_name)
    principal_arn = get_principal_arn(tags)
    synapse_username = get_synapse_user_name(principal_arn)
    tags = add_owner_email_tag(tags, synapse_username)
    client = get_s3_client()
    client.put_bucket_tagging(
      Bucket=bucket_name,
      Tagging={ 'TagSet': tags }
      )

  except Exception as e:
    traceback.print_exc()
    response['status'] = 'failure'
    response['errorMessage'] = str(e)

  return response
