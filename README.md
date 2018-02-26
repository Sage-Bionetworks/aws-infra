# Overview
Scripts for building out and maintaining Sage Bionetworks
infrastructure on AWS

## Create bootstrap and essential resources

```
aws --profile admincentral.root --region us-east-1 \
cloudformation create-stack --stack-name bootstrap \
--capabilities CAPABILITY_NAMED_IAM \
--template-body file://cf_templates/bootstrap.yml

aws --profile admincentral.travis --region us-east-1 \
cloudformation create-stack --stack-name essentials \
--capabilities CAPABILITY_NAMED_IAM \
--template-body file://cf_templates/essentials.yml \
--parameters \
ParameterKey=OperatorEmail,ParameterValue="foo@sagebase.org" \
ParameterKey=FhcrcVpnCidrip,ParameterValue="40.165.75.0/16"
```

The above should bootstrap resources and setup essential resources for new sage
accounts.  Once the resources has been setup you can access and view the account
using the AWS console[1].

## Create VPC

```
aws --profile admincentral.travis --region us-east-1 \
cloudformation update-stack --stack-name my-vpc \
--capabilities CAPABILITY_NAMED_IAM \
--template-body file://cf_templates/vpc.yml \
--parameters \
ParameterKey=VpcName,ParameterValue="my-vpc" \
ParameterKey=VpcSubnetPrefix,ParameterValue="192.150"
```

The above should create a custom VPC with a public and private subnet in
multiple availability zones.

## Continuous Integration
We have configured Travis to deploy CF template to an S3 bucket.


# Contributions

## Issues
* https://sagebionetworks.jira.com/projects/IT

## Builds
* https://travis-ci.org/Sage-Bionetworks/aws-infra

## Secrets
* We use git-crypt[3] to hide secrets.  Access to secrets is tightly controlled.  You will be required to
have your own GPG key[4] and you must request access by a maintainer of this project.



# References

[1] https://AWS-account-ID-or-alias.signin.aws.amazon.com/console

[2] https://github.com/Sage-Bionetworks/Bridge-infra

[3] https://github.com/AGWA/git-crypt

[4] https://help.github.com/articles/generating-a-new-gpg-key
