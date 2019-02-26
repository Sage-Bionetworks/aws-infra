# Overview
This project contains shared templates for building out and maintaining the
Sage Bionetworks infrastructure on AWS.


## Validation
We have setup cfn-lint to validate templates on every pull request.

## Tests
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

