#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

AWS_REGION=eu-west-1
WORKING_DIR=target/it
mkdir -p ${WORKING_DIR}

function set_function_name_from_stack {
    RDS_LOG_DOG_FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name ${FUNCTION_STACK_NAME} | jq -r '.[]|.[].Outputs
    |.[]|select(.OutputKey=="name")|.OutputValue')
}

set_function_name_from_stack

echo "[INFO] invoking lambda (${RDS_LOG_DOG_FUNCTION_NAME}) .."
aws lambda invoke \
      --function-name ${RDS_LOG_DOG_FUNCTION_NAME} \
      --region ${AWS_REGION} \
      --log-type Tail \
      ${WORKING_DIR}/lambda_out.log > ${WORKING_DIR}/lambda_invoke_out

FUNCTION_ERROR=$(cat ${WORKING_DIR}/lambda_invoke_out |jq -r ".FunctionError")

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

echo "------------------------------------- BEGIN log stream events -----------"
echo ${LOG_STREAM_EVENTS_JSON} | jq -r ".events | map(.message) | .[]"
echo "------------------------------------- END log stream events -----------"
echo

if [ ${FUNCTION_ERROR} == "null" ]; then
    echo "[RESULT] OK - lambda execution"
else
    echo "dump logs from invokation (${WORKING_DIR}/it):"
    echo "------------------------------------- BEGIN invocation logs -----------"
    cat ${WORKING_DIR}/lambda_out.log
    echo "---------"
    cat ${WORKING_DIR}/lambda_invoke_out
    echo "------------------------------------- END invocation logs -----------"
    echo 
    echo "[RESULT] ERROR in lambda execution"
    exit 2
fi
