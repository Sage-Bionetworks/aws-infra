#!/usr/bin/env bash

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query 'Account')

S3_TARGET_DIR="s3://bridge-cloudformation-artifacts-$AWS_ACCOUNT_ID/$STACK_NAME/"
echo -e "\nUploading cf_templates to $S3_TARGET_DIR"
aws s3 cp --recursive cf_templates $S3_TARGET_DIR

TEMPLATE_URL="https://s3.amazonaws.com/bridge-cloudformation-artifacts-$AWS_ACCOUNT_ID/$STACK_NAME/bridge.yml"
echo -e "\nValidating CF template $TEMPLATE_URL"
aws cloudformation validate-template --template-url $TEMPLATE_URL

echo -e "\nDeploying CF template $TEMPLATE_URL"
# Handle message that shouldn't be an error, https://github.com/hashicorp/terraform/issues/5653
UPDATE_CMD="./update_cf_stack.sh $TEMPLATE_URL"
message=$($UPDATE_CMD 2>&1 1>/dev/null)
error_code=$(echo $?)
if [[ $error_code -ne 0 && $message =~ .*"No updates are to be performed".* ]]; then
  echo -e "\nNo stack changes detected. An update is not required."
  error_code=0
else
  echo $message
fi
exit $error_code
