#! /bin/bash

set -ex

lambda_dirs=($(ls lambdas/* -d))
for base_dir in "${lambda_dirs[@]}"
do
  build_dir="lambdas/build/${base_dir##*/}"
  template="${base_dir}/template.yaml"
  sam build --build-dir "$build_dir" --base-dir "$base_dir" --template "$template"
done
