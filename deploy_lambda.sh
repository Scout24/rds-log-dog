#!/usr/bin/env bash

# 
# (build and) deploy lambda 
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

DST_BUCKET_STACK_NAME="${DST_BUCKET_STACK_NAME:-rds-log-dog-s3}"

S3_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${DST_BUCKET_STACK_NAME} | jq -r '.[]|.[].Outputs|.[]|select(.OutputKey=="name")|.OutputValue')

echo "deploying to bucket: ${S3_BUCKET_NAME}"
pyb -X -P bucket_name="${S3_BUCKET_NAME}" -x verify upload_zip_to_s3

