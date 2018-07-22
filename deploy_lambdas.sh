#!/bin/bash
set -e

# upload lambda packages to S3 bucket to share
REPO_NAME=${PWD##*/}
S3_BUCKET=$(aws cloudformation list-exports --query "Exports[?Name=='us-east-1-essentials-LambdaArtifactsBucket'].Value" --output text)
S3_BUCKET_PATH="$REPO_NAME/$TRAVIS_BRANCH"

LAMBDA_ROOT_DIR=lambdas
rm -rf $LAMBDA_DIR/*.zip
LAMBDA_DIRS=$(ls -d $LAMBDA_ROOT_DIR/*)
for lambda_dir in $LAMBDA_DIRS
do
  lambda_name="${lambda_dir##*/}"
  lambda_package="${lambda_name}.zip"
  echo -e "\nPackaging lambda ${lambda_name}"
  pushd $LAMBDA_ROOT_DIR/${lambda_name}
  zip -r ../${lambda_package} *
  popd
  echo -e "\nUploading lambda package to s3://$S3_BUCKET/$S3_BUCKET_PATH/${lambda_package}"
  aws s3 cp $LAMBDA_ROOT_DIR/${lambda_package} s3://$S3_BUCKET/$S3_BUCKET_PATH/${lambda_package}
done
