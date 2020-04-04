#! /bin/bash

set -ex

artifacts_bucket=essentials-awss3lambdaartifactsbucket-x29ftznj6pqw
lambda_dirs=($(ls lambdas/* -d))
for base_dir in "${lambda_dirs[@]}"
do
  template="${base_dir}/template.yaml"
  output_template_file="templates/${base_dir##*/}.yaml"
  sam package --template-file "$template" --s3-bucket "$artifacts_bucket" \
    --output-template-file "$output_template_file"
done
