#!/usr/bin/env bash

FILES=cf_templates/*
for f in $FILES
do
  echo -e "\nValidating CF template $f"
  aws cloudformation validate-template --template-body file://$f
done

S3_TARGET_DIR="s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/$TRAVIS_BRANCH/"
echo -e "\nUploading cf_templates to $S3_TARGET_DIR"
aws s3 cp --recursive cf_templates $S3_TARGET_DIR
