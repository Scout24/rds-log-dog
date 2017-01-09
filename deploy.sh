#!/usr/bin/env bash

# 
# build, test and deploy
#

# To make a personal test env:
# - duplicate the templates in cfn
# - change the stack names (e.g. add your username)
# - provide a BUILD_NUMBER (see below in script)
# - call this script with:
# $> 
show_developer_hints() {
  cat << HELP
  export MAIN_STACK_TEMPLATE_NAME=rds-log-dog-${USER:0:3}.yaml 
  export DST_BUCKET_STACK_NAME=rds-log-dog-s3-${USER:0:3}
  export FUNCTION_STACK_TEMPLATE_NAME=rds-log-dog-lambda-${USER:0:3}.yaml
  export FUNCTION_STACK_NAME=rds-log-dog-lambda-${USER:0:3}
  export BUILD_NUMBER="${USER:0:3}-$(date +%s)"
  ./deploy.sh -ci -v
HELP
}

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

# Usage info
show_help() {
    cat << EOF
Usage: ${0##*/} [-hv] [-ci]
    Build and deploy everything. You should specify what to deploy (code, infrastructure)
    Specify at least one of -c or -i.

    -c 		build and deploy lambda function. Can be used with -i too.
    -d          delete needed enviroment variables. cleanup. defaults are used.
    -h          display this help and exit
    -i          deploy infrastructure. Can be used with -c too.
    -v          verbose mode. 
    
    hints for developer:
EOF
show_developer_hints
}

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=false
cleanup=false
DEPLOY_INFRASTRUCTURE=false
DEPLOY_CODE=false

while getopts "h?vicd" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=true
        ;;
    d)  cleanup=true
        ;;
    i)  DEPLOY_INFRASTRUCTURE=true
        ;;
    c)  DEPLOY_CODE=true
        ;;
    esac
done

shift $((OPTIND-1))

if [ ${DEPLOY_INFRASTRUCTURE} == false ] && [ ${DEPLOY_CODE} == false ]; then
    show_help
    exit 0
fi

# check preconditions
command -v cf >/dev/null 2>&1 || { echo >&2 "I require cfn-sphere but it's not installed. Install with: pip install cfn-sphere. Aborting."; exit 1; }

command -v jq >/dev/null 2>&1 || { echo >&2 "I require jq but it's not installed. Install with: apt-get install jq . (or on mac: brew install jq). Aborting."; exit 1; }

function cleanup_env {
    unset MAIN_STACK_TEMPLATE_NAME
    unset DST_BUCKET_STACK_NAME
    unset FUNCTION_STACK_TEMPLATE_NAME
    unset FUNCTION_STACK_NAME
    unset BUILD_NUMBER
}

# ---------------------------------------
# CONFIG
# ---------------------------------------

if [ ${cleanup} == true ]; then
    cleanup_env
fi

# the main cfn template with policies and s3 bucket
MAIN_STACK_TEMPLATE_NAME="${MAIN_STACK_TEMPLATE_NAME:-rds-log-dog-s3.yaml}"

# this is the name of the stack defined in MAIN_STACK_TEMPLATE_NAME
DST_BUCKET_STACK_NAME="${DST_BUCKET_STACK_NAME:-rds-log-dog-s3}"

# cfn template for the lambda function stack
FUNCTION_STACK_TEMPLATE_NAME="${FUNCTION_STACK_TEMPLATE_NAME:-rds-log-dog-lambda.yaml}"

# cfn stack name for the lambda function stack
FUNCTION_STACK_NAME="${FUNCTION_STACK_NAME:-rds-log-dog-lambda}"

BUILD_NUMBER="${BUILD_NUMBER:-0}"
# ---------------------------------------


if [ ${verbose} == true ]; then
    cat << EOF
executing deploy using:
MAIN_STACK_TEMPLATE_NAME:     ${MAIN_STACK_TEMPLATE_NAME}
DST_BUCKET_STACK_NAME:        ${DST_BUCKET_STACK_NAME}
FUNCTION_STACK_TEMPLATE_NAME: ${FUNCTION_STACK_TEMPLATE_NAME}
FUNCTION_STACK_NAME:          ${FUNCTION_STACK_NAME}
BUILD_NUMBER:                 ${BUILD_NUMBER}
EOF
fi

echo "deploying INFRASTRUCTURE ..."
if [ ${DEPLOY_INFRASTRUCTURE} == true ]; then
  (cd cfn/; cf sync -y ${MAIN_STACK_TEMPLATE_NAME})
else
  echo "SKIP!"
fi

function set_target_s3_key_for_lambda {
    local version=$(cat target/VERSION)
    local zipfile=$(ls target/ | grep -e '.zip$')
    S3_KEY_FOR_LAMBDA="dist/v${version}/${zipfile}"
}

echo "deploying CODE ..."
if [ ${DEPLOY_CODE} == true ]; then
    S3_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${DST_BUCKET_STACK_NAME} | jq -r '.[]|.[].Outputs|.[]|select(.OutputKey=="name")|.OutputValue')

    echo "deploying lambda zip to bucket: ${S3_BUCKET_NAME}"
    pyb -X -P bucket_name="${S3_BUCKET_NAME}" -x verify upload_zip_to_s3 

    echo "deploying/update lambda function ..."
    set_target_s3_key_for_lambda 
    (cd cfn/; cf sync -y ${FUNCTION_STACK_TEMPLATE_NAME} -p ${FUNCTION_STACK_NAME}.s3key=${S3_KEY_FOR_LAMBDA})
else
   echo "SKIP!"
fi

