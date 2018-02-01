#!/usr/bin/env bash

TEMPLATE_URL=$1

aws cloudformation update-stack \
--stack-name $STACK_NAME \
--capabilities CAPABILITY_NAMED_IAM \
--notification-arns $CloudformationNotifyLambdaTopicArn \
--template-url $TEMPLATE_URL \
--parameters \
ParameterKey=AwsAccountId,ParameterValue=$AwsAccountId \
ParameterKey=AwsDefaultVpcId,ParameterValue=$AwsDefaultVpcId \
ParameterKey=AwsVpcSubnetPrefix,ParameterValue=$AwsVpcSubnetPrefix \
ParameterKey=FhcrcVpnCidrip,ParameterValue=$FhcrcVpnCidrip \
ParameterKey=OperatorEmail,ParameterValue=$OperatorEmail
