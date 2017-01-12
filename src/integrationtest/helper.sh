
AWS_REGION=eu-west-1
WORKING_DIR=target/it
mkdir -p ${WORKING_DIR}

function set_function_name_from_stack {
    RDS_LOG_DOG_FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name ${FUNCTION_STACK_NAME} | jq -r '.[]|.[].Outputs
    |.[]|select(.OutputKey=="name")|.OutputValue')
}


