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

echo "[INFO] invoking lambda (${RDS_LOG_DOG_FUNCTION_NAME}) .."
aws lambda invoke \
      --function-name ${RDS_LOG_DOG_FUNCTION_NAME} \
      --region eu-west-1 \
      --log-type Tail \
      out.log > out

FUNCTION_ERROR=$(cat out |jq -r ".FunctionError")

echo "[INFO] getting the logs from cloudwatch ..."
LOG_GROUP_NAME="/aws/lambda/${RDS_LOG_DOG_FUNCTION_NAME}"
LOG_STREAM_NAME=$(
aws logs describe-log-streams --log-group-name=${LOG_GROUP_NAME} \
      | jq -r ".logStreams[0].logStreamName"
)
LOG_STREAM_EVENTS_JSON=$(
  aws logs get-log-events \
    --log-group-name=${LOG_GROUP_NAME} \
    --log-stream-name=${LOG_STREAM_NAME}
)

echo ${LOG_STREAM_EVENTS_JSON} | jq -r ".events | map(.message) | .[]"

if [ ${FUNCTION_ERROR} == "null" ]; then
    echo "[RESULT] OK - lambda execution"
else
    echo "[RESULT] ERROR in lambda execution"
    exit 2
fi
