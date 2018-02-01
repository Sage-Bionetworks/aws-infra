#!/usr/bin/env bash

# normalize env vars with by git branch
eval export "AwsAccountId=\$AwsAccountId_$TRAVIS_BRANCH"
eval export "AwsDefaultVpcId=\$AwsDefaultVpcId_$TRAVIS_BRANCH"
eval export "AwsVpcSubnetPrefix=\$AwsVpcSubnetPrefix_$TRAVIS_BRANCH"
eval export "OperatorEmail=\$OperatorEmail_$TRAVIS_BRANCH"
eval export "FhcrcVpnCidrip=\$FhcrcVpnCidrip_$TRAVIS_BRANCH"
eval export "SSLCertArn=\$SSLCertArn_$TRAVIS_BRANCH"
