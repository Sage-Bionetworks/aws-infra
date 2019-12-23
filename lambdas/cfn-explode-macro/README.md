# Explode CloudFormation Macro

The `Explode` macro provides a template-wide `Explode` property for CloudFormation resources. Similar to the Count
macro, it will create multiple copies of a template Resource, but looks up values to inject into each copy in a
Mapping or a Parameter.

## How to install and use the Explode macro in your AWS account

### Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts. If you don't have one already, create one
with `aws s3 mb s3://<bucket name>`

2. Build the lambda

```shell
sam build \
    --build-dir lambdas/build/cfn-explode-macro \
    --base-dir lambdas/cfn-explode-macro \
    --template lambdas/cfn-explode-macro/template.yaml
```

3. Package the Macro and deploy it to a S3 bucket

```shell
sam package \
    --template-file lambdas/build/cfn-explode-macro/template.yaml \
    --output-template-file templates/cfn-explode-macro.yaml
    --s3-bucket <bucket name> \
```

4. Deploy the packaged CloudFormation template to a CloudFormation stack:

```shell
sam deploy \
    --stack-name cfn-explode-macro \
    --template-file templates/cfn-explode-macro.yaml \
    --capabilities CAPABILITY_IAM
```

5. To test out the macro's capabilities, try launching the provided example template in the
Mapping or Parameters section:

```shell
aws cloudformation deploy \
    --stack-name test-ExplodeParam \
    --template-file ExampleMapping.yaml \
    --parameters ParameterKey=Ports,ParameterValue=["22","80"] \
    --capabilities CAPABILITY_IAM
```

### Usage

To make use of the macro, add `Transform: Explode` to the top level of your CloudFormation template.

#### Mapping

Add a mapping (to the `Mappings` section of your template) which contains the instances of the resource values you want to use. Each entry in the mapping will be used for another copy of the resource, and the values inside it will be copied into that instance. The entry name will be appended to the template resource name, unless a value `ResourceName` is given, which if present will be used as the complete resource name.

For the resource you want to explode, add an `ExplodeMap` value at the top level pointing at the entry from your Mappings which should be used. You can use the same mapping against multiple resource entries.

Inside the resource properties, you can use `!Explode KEY` to pull the value of `KEY` out of your mapping.

An example is probably in order:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: Explode
Mappings:
  BucketMap:
    Monthly:
      ResourceName: MyThirtyDayBucket
      Retention: 30
    Yearly:
      Retention: 365

Resources:
  Bucket:
    ExplodeMap: BucketMap
    Type: AWS::S3::Bucket
    Properties:
      LifecycleConfiguration:
        Rules:
          -
            ExpirationInDays: !Explode Retention
            Status: Enabled
```

This will result in two Bucket resources; one named `MyThirtyDayBucket` with a
lifecycle rule for 30 day retention, and another named `BucketYearly` with 365
day retention.

#### Parameters

Add a list parameter (to the `Parameters` section of your template) which contains the instances of the resource values
you want to use.  Each entry in the list will be used for another copy of the resource, and the values inside it will
be copied into that instance.  The entry name will be appended to the template resource name.

For the resource you want to explode, add an `ExplodeParam` value at the top level pointing at the entry for your
Parameter which should be used.

Inside the resource properties, us the singular name of the parameter `!Explode KEY`.

An example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: Explode
Parameters:
  Ports:
    Description: The ports to open
    Type: List<Number>
    Default: "[]"

Resources:
  SecurityGroup:
    ExplodeParam: Ports
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: "Instance security group"
      SecurityGroupIngress:
        - CidrIp: "0.0.0.0/0"
          FromPort: "!Explode Port"
          ToPort: "!Explode Port"
          IpProtocol: tcp
```

The mumber of list values passed to the parameter will generate an equivalent number of security group resources.
If `--parameters  ParameterKey=Ports,ParameterValue=["22","80"]` is passed in the result will be two security group
resources; one named `SecurityGroupPort22`, and another named `SecurityGroupPort80`.


### Important - Naming resources

You cannot use Explode on resources that use a hardcoded name (`Name:`
property). Duplicate names will cause a CloudFormation runtime failure.
If you wish to specify a name then you must use `!Explode` with a mapped value
to make each resource's name unique.

For example:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Mappings:
  BucketMap:
    Example:
      Name: MyExampleBucket
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    ExplodeMap: BucketMap
    Properties:
        BucketName: !Explode Name
```

### Linting
Using [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint) to validate cloudformation templates containing
macros may fail however the templates are completely valid and will work as long as the lamba macro has been deployed to
AWS. Add this to your templates to supress linter errors:

```yaml
Metadata:
  cfn-lint:
    config:
      ignore_checks:
      - E3001
      - E3012
      - W7001
      - W2001
```
### Testing

#### Unit tests
 1. pip install jsondiff
 2. cd lambdas/cfn-explode-macro
 3. run `python -m pytest tests/ -v`

#### SAM local tests
1. Build the lambda
2. cd lambdas/build/cfn-explode-macro
3. pip install jq
4. run

```shell
sam local invoke MacroFunction \
    --template lambdas/build/cfn-explode-macro/template.yaml
    --event lambdas/cfn-explode-macro/tests/events/explode_map.json|jq .
```
Then verify the output is what you expect

## Author

[James Seward](https://github.com/jamesoff); AWS Solutions Architect, Amazon Web Services

[Khai Do](https://github.com/zaro0508); Cloud Architect, Sage Bionetworks
