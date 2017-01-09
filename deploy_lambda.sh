#!/usr/bin/env bash

# 
# (build and) deploy lambda 
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

# check preconditions
command -v cf >/dev/null 2>&1 || { echo >&2 "I require cfn-sphere but it's not installed. Install with: pip install cfn-sphere. Aborting."; exit 1; }

DST_BUCKET_STACK_NAME="${DST_BUCKET_STACK_NAME:-rds-log-dog-s3}"
STACK_TEMPLATE_NAME="${STACK_NAME:-rds-log-dog-lambda.yaml}"

S3_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${DST_BUCKET_STACK_NAME} | jq -r '.[]|.[].Outputs|.[]|select(.OutputKey=="name")|.OutputValue')

echo "deploying lambda zip to bucket: ${S3_BUCKET_NAME}"
pyb -X -P bucket_name="${S3_BUCKET_NAME}" -x verify upload_zip_to_s3 lambda_release

echo "deploying/update lambda function ..."
(cd cfn/; cf sync -y ${STACK_TEMPLATE_NAME})

