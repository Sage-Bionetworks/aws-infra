# Overview
This project contains shared templates for building out and maintaining the
Sage Bionetworks infrastructure on AWS.

## Contributions
Contributions are welcome.

Requirements:
* Install [pre-commit](https://pre-commit.com/#install) app
* Clone this repo
* Run `pre-commit install` to install the git hook.

## Testing
As a pre-deployment step we syntatically validate our packer json
files with [pre-commit](https://pre-commit.com).

Please install pre-commit, once installed the file validations will
automatically run on every commit.  Alternatively you can manually
execute the validations by running `pre-commit run --all-files`.

We have setup [taskcat](https://github.com/aws-quickstart/taskcat) to test
that shared templates can actually deploy resources to our AWS accounts.
The test runs in our Admincentral account.  We only validate on `us-east-1`
region.

## Continuous Integration
We have configured the CI to deploy CF template to a public S3 bucket on the
AWS Admincentral account.  The purpose is to allow us to share those templates.

## Deployments
Templates can be deployed using the AWSCLI.  We use [sceptre](https://github.com/cloudreach/sceptre)
for more functionality.  Examples of deployments can be found in our
other Sage-Bionetworks/*-infa repos
(i.e. [sandbox-infra](https://github.com/Sage-Bionetworks/sandbox-infra))

## Issues
* https://sagebionetworks.jira.com/projects/IT

## Builds
* https://travis-ci.org/Sage-Bionetworks/aws-infra

## Secrets
* We use the [AWS SSM](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html)
to store secrets for this project.  Sceptre retrieves the secrets using
a [sceptre ssm resolver](https://github.com/cloudreach/sceptre/tree/v1/contrib/ssm-resolver)
and passes them to the cloudformation stack on deployment.
