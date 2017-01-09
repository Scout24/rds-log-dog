#!/usr/bin/env bash

# 
# build, test and deploy
#

# To make a personal test env:
# - duplicate the templates in cfn
# - change the stack names (e.g. add your username)
# - call this script with:
# $> 
<<"HELP"
  export MAIN_STACK_TEMPLATE_NAME=rds-log-dog-FBO.yaml 
  export DST_BUCKET_STACK_NAME=rds-log-dog-s3-FBO
  export FUNCTION_STACK_TEMPLATE_NAME=rds-log-dog-lambda-FBO.yaml
  ./deploy.sh
HELP

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
    -h          display this help and exit
    -i          deploy infrastructure. Can be used with -c too.
    -v          verbose mode. 
EOF
}

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=false
DEPLOY_INFRASTRUCTURE=false
DEPLOY_CODE=false

while getopts "h?vic" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=true
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

# ---------------------------------------
# CONFIG
# ---------------------------------------

# the main cfn template with policies and s3 bucket
MAIN_STACK_TEMPLATE_NAME="${MAIN_STACK_TEMPLATE_NAME:-rds-log-dog-s3.yaml}"

# this is the name of the stack defined in MAIN_STACK_TEMPLATE_NAME
DST_BUCKET_STACK_NAME="${DST_BUCKET_STACK_NAME:-rds-log-dog-s3}"

# cfn template for the lambda function stack
FUNCTION_STACK_TEMPLATE_NAME="${FUNCTION_STACK_TEMPLATE_NAME:-rds-log-dog-lambda.yaml}"

# ---------------------------------------

if [ ${verbose} == true ]; then
    cat << EOF
executing deploy using:
MAIN_STACK_TEMPLATE_NAME:     ${MAIN_STACK_TEMPLATE_NAME}
DST_BUCKET_STACK_NAME:        ${DST_BUCKET_STACK_NAME}
FUNCTION_STACK_TEMPLATE_NAME: ${FUNCTION_STACK_TEMPLATE_NAME}
EOF
fi

echo "deploying INFRASTRUCTURE ..."
if [ ${DEPLOY_INFRASTRUCTURE} == true ]; then
  (cd cfn/; cf sync -y ${MAIN_STACK_TEMPLATE_NAME})
else
  echo "SKIP!"
fi

echo "deploying CODE ..."
if [ ${DEPLOY_CODE} == true ]; then
    S3_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${DST_BUCKET_STACK_NAME} | jq -r '.[]|.[].Outputs|.[]|select(.OutputKey=="name")|.OutputValue')

    echo "deploying lambda zip to bucket: ${S3_BUCKET_NAME}"
    pyb -X -P bucket_name="${S3_BUCKET_NAME}" -x verify upload_zip_to_s3 lambda_release

    echo "deploying/update lambda function ..."
    (cd cfn/; cf sync -y ${FUNCTION_STACK_TEMPLATE_NAME})
else
   echo "SKIP!"
fi

