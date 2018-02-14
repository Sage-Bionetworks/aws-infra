#!/usr/bin/env bash

# Need to upload TEMPLATES to S3 before validating due to template-body MAX 51K length
# https://docs.aws.amazon.com/cli/latest/reference/cloudformation/validate-template.html#options
S3_BUCKET="bootstrap-awss3cloudformationbucket-19qromfd235z9"
S3_BUCKET_URL="s3://$S3_BUCKET/$TRAVIS_BRANCH"
TEMP_DIR="temp"

# get list of templates
pushd cf_templates
TEMPLATES=*

for f in $TEMPLATES
do
  echo -e "\nUploading cf_templates to $S3_BUCKET_URL/$TEMP_DIR/$f"
  aws s3 cp $f $S3_BUCKET_URL/$TEMP_DIR/$f
done

TEMPLATE_URL="https://s3.amazonaws.com/$S3_BUCKET/$TRAVIS_BRANCH"
for f in $TEMPLATES
do
  echo -e "\nValidating CF template $TEMPLATE_URL/$TEMP_DIR/$f"
  aws cloudformation validate-template --template-url $TEMPLATE_URL/$TEMP_DIR/$f
  aws s3 mv $S3_BUCKET_URL/$TEMP_DIR/$f $S3_BUCKET_URL/$f
done

popd

