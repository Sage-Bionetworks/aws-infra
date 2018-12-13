# Overview
Shared templates for building out and maintaining Sage Bionetworks
infrastructure on AWS.

## Create bootstrap
Bootstrapping the account is a one time manual process:

1. Login to the AWS console with the 'root' account.
2. Goto Services -> Cloudformation
3. Run the bootstrap.yaml template.

* Name it `bootstrap` and accept default for all other parameters.

This will create the required account (i.e. travis) to deploy all
downstream CF templates.

# Initial AWS Account Setup

## Setup AWS CLI
Setup the AWS CLI to setup AWS account from the terminal.

The newly created account (i.e. travis) by itself does not have permissions
to deploy templates.  You must use the travis user credentials to assume
the cfservice role to get permissions to deploy the templates.

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

## Setup AWS account policies
As a best practice we want to set account policies for every one of our AWS accounts.
We have a script to help with that.  Setup the profile in
[set_account_policy.sh](https://github.com/Sage-Bionetworks/infra-utils/blob/master/aws/set_account_policy.sh)
script and execute the it against the AWS account.


## Setup automation for AWS account
We want to automate the management of the AWS account by using git and travis and putting
our cloudformation templates in under CI/CD.

1. Create a new repo in github, the convention is <repo name>-infra (i.e. Sage-Bionetworks/myaws-infra).
2. Fork the repo.
3. Enable travis build on the repo
4. Use one of our existing `Sage-Bionetworks/*-infra` repos as an example, copy files from it to the new repo.
5. Edit files in templates/* and config/* to match your account's purpose.
6. Edit .travis.yml to deploy templates.
7. Edit README.md to describe the purpose of your account.

# Deploy Templates

## Create essential resources

Note: The essentials template will setup log aggregation to
[logcentral](https://github.com/Sage-Bionetworks/logcentral-infra).  A
pre-requesite for running this template is setup log aggregation from
the the new account into logcentral.

1. Due to issue [IT-418](https://sagebionetworks.jira.com/browse/IT-418) you will
need to replace the value of parameter `VpcPeeringRequesterAwsAccountId` from
`!ssm /infra/AdmincentralAwsAccountId` to the actual account id (i.e. 234567891234). 
2. Now execute the template
```
 curl https://raw.githubusercontent.com/Sage-Bionetworks/aws-infra/master/templates/essentials.yaml --create-dirs -o remote-templates/essentials.yaml
 sceptre --var "profile=myaws.cfservice" --var "region=us-east-1" launch-stack prod essentials
```

The above should setup essential resources for new sage AWS accounts.  Once
the resources have been setup you can access and view the account using the
[AWS console](https://AWS-account-ID-or-alias.signin.aws.amazon.com/console).

## Create VPC
Creating a VPC is optional, some accounts do not need a custom VPC.  Typically you will
want to create a VPC if you want to run apps in a VPC.  We use a custom
[vpc.yaml](templates/vpc.yaml) template to create VPCs.

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
 curl https://raw.githubusercontent.com/Sage-Bionetworks/aws-infra/master/templates/essentials.yaml --create-dirs -o remote-templates/essentials.yaml
 sceptre --var "profile=myaws.cfservice" --var "region=us-east-1" launch-stack prod peer-vpn-myaccount
```

The above should configure the public and private routes for the VPC with
the peering connection to the VPN.  That allows the VPN to direct traffic
to this VPC.


## Continuous Integration
We have configured Travis to deploy CF template updates.  Travis deploys using
[sceptre](https://sceptre.cloudreach.com/latest/about.html)

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

