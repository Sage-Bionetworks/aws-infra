#!/bin/bash
set -e

# Deploy templates to AWS Admincentral account to share with other projects.
REPO_NAME="${PWD##*/}"
S3_BUCKET=$(aws cloudformation list-exports --query "Exports[?Name=='us-east-1-bootstrap-CloudformationBucket'].Value" --output text)
S3_BUCKET_PATH="$REPO_NAME/$TRAVIS_BRANCH"
S3_BUCKET_URL="s3://$S3_BUCKET/$S3_BUCKET_PATH"

# Upload local templates
TEMPLATES=templates/*
for template in $TEMPLATES
do
  dir="${template%/*}"
  file="${template##*/}"
  extension="${file##*.}"
  filename="${file%.*}"
  aws s3 cp ${template} $S3_BUCKET_URL/${file}
done
