# Overview
Shared templates for building out and maintaining Sage Bionetworks
infrastructure on AWS.

## Create bootstrap
Bootstrapping the account is a one time manual process:

1. Login to the AWS console with the 'root' account.
2. Goto Services -> Cloudformation
3. Run the bootstrap.yaml template

This will create the account (i.e. travis) required to deploy other
CF templates.

## Deploying templates

The travis account by itself does not have permissions to deploy templates.
You must use the travis user credentials to assume the cfservice role to
get permissions to deploy the templates.

1. Setup ~/.aws/credentials file
```
[default]
region = us-east-1
[bridge.dev.travis]
aws_access_key_id = <Access Key>
aws_secret_access_key = <Secret Access Key>
```

2. Setup ~/.aws/config file
```
[default]
region = us-east-1
[profile bridge.dev.cfservice]
role_arn = <CF Service Role Arn>
source_profile = bridge.dev.travis
```
__NOTE__- source_profile needs to match the profile in ~/.aws/credentials file

4. Assume CF service role to deploy templates
```
aws --profile bridge.dev.cfservice --region us-east-1 cloudformation create-stack ...
```

## Create essential resources

Note: The essentials template will setup log aggregation to
[logcentral](https://github.com/Sage-Bionetworks/logcentral-infra).  A
pre-requesite for running this template is setup log aggregation from
the the new account into logcentral.

```
aws --profile bridge.dev.cfservice --region us-east-1 \
cloudformation create-stack --stack-name essentials \
--capabilities CAPABILITY_NAMED_IAM \
--template-url https://s3.amazonaws.com/bootstrap-awss3cloudformationbucket-19qromfd235z9/aws-infra/master/essentials.yaml \
--parameters \
ParameterKey=OperatorEmail,ParameterValue="foo@sagebase.org" \
ParameterKey=VpcPeeringRequesterAwsAccountId,ParameterValue="123456789012""
```

The above should setup essential resources for new sage accounts.  Once
the resources has been setup you can access and view the account using the
[AWS console](https://AWS-account-ID-or-alias.signin.aws.amazon.com/console).

## Create VPC

```
aws --profile bridge.dev.cfservice --region us-east-1 \
cloudformation create-stack --stack-name vpc-bridge-develop \
--capabilities CAPABILITY_NAMED_IAM \
--template-url https://s3.amazonaws.com/bootstrap-awss3cloudformationbucket-19qromfd235z9/aws-infra/master/vpc.yaml \
--parameters \
ParameterKey=VpcName,ParameterValue="vpc-bridge-develop" \
ParameterKey=VpcSubnetPrefix,ParameterValue="172.150"
```

The above should create a custom VPC with a public and private subnet in
multiple availability zones.

## Configure VPC peering to VPN

`Important` - This template must be run in sequence and can only be run after
the peering connection has been created.  To create the peering connnection run the
[VPCPeer.yaml](https://github.com/Sage-Bionetworks/admincentral-infra/blob/master/templates/VPCPeer.yaml)
template.

The sequence:
1. Create VPC by running [vpc.yaml](./vpc.yaml) template
2. Setup VPC peering connection by running VPCPeer.yaml
3. Configure the VPC public and private route table with [vpc.yaml](./vpc.yaml) template

```
aws --profile bridge.dev.cfservice --region us-east-1 \
cloudformation create-stack --stack-name peer-vpn-bridge-develop \
--capabilities CAPABILITY_NAMED_IAM \
--template-url https://s3.amazonaws.com/bootstrap-awss3cloudformationbucket-19qromfd235z9/aws-infra/master/peer-route-config.yaml \
--parameters \
ParameterKey=PeeringConnectionId,ParameterValue="pcx-eb02e083" \
ParameterKey=VpcPublicRouteTable,ParameterValue="rtb-f1a9698d" \
ParameterKey=VpcPrivateRouteTable,ParameterValue="rtb-bbb878c7"
```

The above should configure the public and private routes for the VPC with
the peering connection to the VPN.  That allows the VPN to direct traffic
to this VPC.

## Validation
We have setup the CI to syntax validate cloudformation templates with cfn-lint.

## Tests
We have setup the CI to test cloudformation templates with
[taskcat](https://github.com/aws-quickstart/taskcat).  Tests get run in the
AWS Admincentral account.

## Continuous Integration
We have configured the CI to deploy CF template to an S3 bucket on the
AWS Admincentral account.

# Contributions

## Issues
* https://sagebionetworks.jira.com/projects/IT

## Builds
* https://travis-ci.org/Sage-Bionetworks/aws-infra

## Secrets
* We use the [AWS SSM](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html)
to store secrets for this project.  Sceptre retrieves the secrets using
a [sceptre ssm resolver](https://github.com/cloudreach/sceptre/tree/v1/contrib/ssm-resolver)
and passes them to the cloudformation stack on deployment.

