# Explode CloudFormation Macro

The `Explode` macro provides a template-wide `Explode` property for CloudFormation resources. Similar to the Count macro, it will create multiple copies of a template Resource, but looks up values to inject into each copy in a Mapping.

## How to install and use the Explode macro in your AWS account

### Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts. If you don't have one already, create one with `aws s3 mb s3://<bucket name>`

2. Package the Macro CloudFormation template. The provided template uses [the AWS Serverless Application Model](https://aws.amazon.com/about-aws/whats-new/2016/11/introducing-the-aws-serverless-application-model/) so must be transformed before you can deploy it.

```shell
aws cloudformation package \
    --template-file macro.yml \
    --s3-bucket <your bucket name here> \
    --output-template-file packaged.yaml
```

3. Deploy the packaged CloudFormation template to a CloudFormation stack:

```shell
aws cloudformation deploy \
    --stack-name Explode-macro \
    --template-file packaged.yaml \
    --capabilities CAPABILITY_IAM
```

4. To test out the macro's capabilities, try launching the provided example template:

```shell
aws cloudformation deploy \
    --stack-name Explode-test \
    --template-file test.yaml \
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

Inside the resource properties, us the singular name of the parameter `!Explode KEY` to .

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
      SecurityGroupEgress:
        - CidrIp: "0.0.0.0/0"
          FromPort: -1
          ToPort: -1
          IpProtocol: "-1"
```

The mumber of list values passed to the parameter will generate an equivalent number of security group resources.
If `Port=[22,80]` then this will result in two security group resources; one named `SecurityGroupPort22`,
and another named `SecurityGroupPort80`.


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
```

## Author

[James Seward](https://github.com/jamesoff); AWS Solutions Architect, Amazon Web Services

[Khai Do](https://github.com/zaro0508); Cloud Architect, Sage Bionetworks
