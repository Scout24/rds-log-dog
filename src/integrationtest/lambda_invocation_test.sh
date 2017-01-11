#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

function set_function_name_from_stack {
    RDS_LOG_DOG_FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name ${FUNCTION_STACK_NAME} | jq -r '.[]|.[].Outputs
    |.[]|select(.OutputKey=="name")|.OutputValue')
}

set_function_name_from_stack

aws lambda invoke \
      --invocation-type RequestResponse \
      --function-name ${RDS_LOG_DOG_FUNCTION_NAME} \
      --region eu-west-1 \
      --log-type Tail \
      --payload '{"region": "eu-west-1", "bucket_name": "YOUR_BUCKET_NAME", "s3_host": "s3.amazonaws.com"}' \
      lambda.log

