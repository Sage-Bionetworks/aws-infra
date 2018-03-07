# Overview
Scripts for building out and maintaining Sage Bionetworks
infrastructure on AWS

## Create bootstrap
Bootstrapping the account is a one time manual process:

1. Login to the AWS console with the 'root' account.
2. Goto Services -> Cloudformation
3. Run the bootstrap.yml template

This will create the admin account (i.e. travis) required to run other
CF templates.

## Create essential resources

```
aws --profile bridge.dev.travis --region us-east-1 \
cloudformation create-stack --stack-name essentials \
--capabilities CAPABILITY_NAMED_IAM \
--template-body file://cf_templates/essentials.yml \
--parameters \
ParameterKey=OperatorEmail,ParameterValue="foo@sagebase.org" \
ParameterKey=FhcrcVpnCidrip,ParameterValue="40.165.75.0/16"
```

The above should setup essential resources for new sage accounts.  Once
the resources has been setup you can access and view the account using the
[AWS console](https://AWS-account-ID-or-alias.signin.aws.amazon.com/console).

## Create VPC

```
aws --profile bridge.dev.travis --region us-east-1 \
cloudformation update-stack --stack-name vpc-bridge-develop \
--capabilities CAPABILITY_NAMED_IAM \
--template-body file://cf_templates/vpc.yml \
--parameters \
ParameterKey=VpcName,ParameterValue="my-vpc" \
ParameterKey=VpcSubnetPrefix,ParameterValue="192.150"
```

The above should create a custom VPC with a public and private subnet in
multiple availability zones.

## Configure VPC peering to VPN

`Important` - This template must be run in sequence and can only be run after
the peering connection has been created.  To create the peering connnection run the
[VPCPeer.yml](https://github.com/Sage-Bionetworks/admincentral-infra/blob/master/cf_templates/VPCPeer.yml)
template.

The sequence:
1. Create VPC by running [vpc.yml](./vpc.yml) template
2. Setup VPC peering connection by running VPCPeer.yml
3. Configure the VPC public and private route table with [vpc.yml](./vpc.yml) template

```
aws --profile bridge.dev.travis --region us-east-1 \
cloudformation update-stack --stack-name peer-vpc-bridge-develop \
--capabilities CAPABILITY_NAMED_IAM \
--template-body file://cf_templates/peer-route-config.yml \
--parameters \
ParameterKey=PeeringConnectionId,ParameterValue="pcx-eb02e083" \
ParameterKey=VpcPublicRouteTable,ParameterValue="rtb-f1a9698d" \
ParameterKey=VpcPrivateRouteTable,ParameterValue="rtb-bbb878c7"
```

The above should configure the public and private routes for the VPC with
the peering connection to the VPN.  That allows the VPN to direct traffic
to this VPC.


## Continuous Integration
We have configured Travis to deploy CF template to an S3 bucket.


# Contributions

## Issues
* https://sagebionetworks.jira.com/projects/IT

## Builds
* https://travis-ci.org/Sage-Bionetworks/aws-infra

## Secrets
* We use [git-crypt](https://github.com/AGWA/git-crypt) to hide secrets.
  Access to secrets is tightly controlled.  You will be required to have
  your own [GPG key](https://help.github.com/articles/generating-a-new-gpg-key)
  and you must request access by a maintainer of this project.

