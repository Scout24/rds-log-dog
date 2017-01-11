#!/usr/bin/env bash

#
# build, test and deploy
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

source helper.sh

# Usage info
show_help() {
    cat << EOF
Usage: ${0##*/} [-hv] [-ci] [-s:]
    Build and deploy everything. You should specify what to deploy (code, infrastructure)
    Specify at least one of -c or -i.

    -c 		build and deploy lambda function. Can be used with -i too.
    -d          delete needed enviroment variables. cleanup. defaults are used.
    -h          display this help and exit
    -i          deploy infrastructure. Can be used with -c too.
    -p          disable personal build/deploy for development 
                normally cloudformation stacks will be suffixed with your local username (3) 
    -v          verbose mode.

    example usage:
    ./deploy.sh -ci
    ./deploy.sh -ci -p      to deploy to production (no personal build)
EOF
}

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=false
cleanup=false
DEPLOY_INFRASTRUCTURE=false
DEPLOY_CODE=false
PERSONAL_BUILD=true

while getopts "h?vicdp" opt; do
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
    p)  PERSONAL_BUILD=false
        ;;
    esac
done

shift $((OPTIND-1))

if [ ${DEPLOY_INFRASTRUCTURE} == false ] && [ ${DEPLOY_CODE} == false ] && [ ${cleanup} == false ]; then
    show_help
    exit 0
fi

# check preconditions
command -v cf >/dev/null 2>&1 || { echo >&2 "I require cfn-sphere but it's not installed. Install with: pip install cfn-sphere. Aborting."; exit 1; }

command -v jq >/dev/null 2>&1 || { echo >&2 "I require jq but it's not installed. Install with: apt-get install jq . (or on mac: brew install jq). Aborting."; exit 1; }

function cleanup_env {
    unset BUILD_NUMBER
}

# ---------------------------------------
# CONFIG
# ---------------------------------------

if [ ${cleanup} == true ]; then
    cleanup_env
fi

[ ${PERSONAL_BUILD} == true ] && ./create_dev_stack.sh
set_templates_and_stack_names
[ ${PERSONAL_BUILD} == true ] && export BUILD_NUMBER=dev.$(date +%Y%m%d%H%M%S)

# ---------------------------------------

if [ ${verbose} == true ]; then
    cat << EOF
executing deploy using:
DST_BUCKET_STACK_NAME:        ${DST_BUCKET_STACK_NAME}
FUNCTION_STACK_NAME:          ${FUNCTION_STACK_NAME}
PERSONAL_BUILD:               ${PERSONAL_BUILD}
BUILD_NUMBER:                 ${BUILD_NUMBER}
EOF
fi

echo "deploying INFRASTRUCTURE ..."
if [ ${DEPLOY_INFRASTRUCTURE} == true ]; then
  (cd cfn/; cf sync -y ${DST_BUCKET_STACK_NAME}.yaml)
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
    (cd cfn/; cf sync -y ${FUNCTION_STACK_NAME}.yaml -p ${FUNCTION_STACK_NAME}.s3key=${S3_KEY_FOR_LAMBDA})
else
   echo "SKIP!"
fi

