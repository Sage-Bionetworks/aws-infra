# cfn-list-transform-macro

The `ListTransform` macro allows the manipulation of a list in a CloudFormation
template. Currently this only supports prepending or appending strings to the
members of a list.

Inventory of source code and supporting files:

- list_transformm - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

## Example
The following contains an example of how to use the transform and the resulting
output.

### Before
This is a segment of a CloudFormation template where security group names are
being added to an EC2 instance using `Fn::Tranform`.

```yaml
Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      SecurityGroups:
        Fn::Transform:
          - Name: ListTransform
            Parameters:
              Operation: TransformList
              TransformString: 'MySecurityGroup'
              List:
                - 22
                - 443
              Prepend: true
```

### After
This is what the template segment will look like after the macro runs:

```yaml
Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      SecurityGroups:
        - MySecurityGroup22
        - MySecurityGroup443
```

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

## Use the SAM CLI to build and test locally

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

Build your application with the `sam build --use-container` command.

```bash
cfn-list-transform-macro$ sam build --use-container
```

The SAM CLI installs dependencies defined in `list_transform/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
cfn-list-transform-macro$ sam local invoke TransformFunction --event events/list_transform_no_prepend.json
```

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
cfn-list-transform-macro$ sam logs -n TransformFunction --stack-name cfn-list-transform-macro --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
cfn-list-transform-macro$ pip install pytest --user
cfn-list-transform-macro$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name cfn-list-transform-macro
```

## Author

[Tess Thyer](https://github.com/tthyer); Sr. Data Engineer, Sage Bionetworks