#!/usr/bin/env bash

#
# build, test and deploy
#
set +o nounset
source helper.sh

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
    -d          delete stacks, and needed enviroment variables.
    -h          display this help and exit
    -i          deploy infrastructure. Can be used with -c too.
    -p          disable personal build/deploy for development
                normally cloudformation stacks will be suffixed with your local username (3)
    -s          deploy scheduler for the lambda. Can be used with -c too.
    -v          verbose mode.

    example usage:
    ./deploy.sh -ci
    ./deploy.sh -ci -p  to deploy to production (no personal build)
    ./deploy.sh -cis    to deploy including a scheduler
                        (attention: scheduler will run the lambda regularly!)
EOF
}

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=false
cleanup=false
DEPLOY_INFRASTRUCTURE=false
DEPLOY_CODE=false
DEPLOY_SCHEDULER=false
PERSONAL_BUILD=true

while getopts "h?vicdps" opt; do
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
    s)  DEPLOY_SCHEDULER=true
        ;;
    esac
done

shift $((OPTIND-1))

if [ ${DEPLOY_INFRASTRUCTURE} == false ] && [ ${DEPLOY_CODE} == false ] && \
   [ "${DEPLOY_SCHEDULER}" == "false" ] && [ ${cleanup} == false ]; then
    show_help
    exit 0
fi

# check preconditions
command -v cf >/dev/null 2>&1 || { echo >&2 "I require cfn-sphere but it's not installed. Install with: pip install cfn-sphere. Aborting."; exit 1; }

command -v jq >/dev/null 2>&1 || { echo >&2 "I require jq but it's not installed. Install with: apt-get install jq . (or on mac: brew install jq). Aborting."; exit 1; }

function cleanup_env {
    set +o nounset
    unset BUILD_NUMBER
    unset DST_BUCKET_STACK_NAME
    unset FUNCTION_STACK_NAME
    unset SCHEDULER_STACK_NAME
    set -o nounset
}

# ---------------------------------------
# CONFIG
# ---------------------------------------

[ ${PERSONAL_BUILD} == true ] && ./create_dev_stack.sh
set_templates_and_stack_names
[ ${PERSONAL_BUILD} == true ] && export BUILD_NUMBER=dev.$(date +%Y%m%d%H%M%S)


if [ ${cleanup} == true ]; then
    if [ ${PERSONAL_BUILD} == true ]; then
        set +o errexit
        (cd cfn/; cf delete -y ${SCHEDULER_STACK_NAME}.yaml && rm ${SCHEDULER_STACK_NAME}.yaml)
        set_dst_s3_bucket_name_from_stack
        (cd cfn/; cf delete -y ${FUNCTION_STACK_NAME}.yaml && rm ${FUNCTION_STACK_NAME}.yaml)
        aws s3 rm --recursive s3://${S3_BUCKET_NAME}/
        (cd cfn/; cf delete -y ${DST_BUCKET_STACK_NAME}.yaml && rm ${DST_BUCKET_STACK_NAME}.yaml)
        rm cfn/.gitignore
    fi
    cleanup_env
    pyb clean
    exit
fi
# ---------------------------------------

function display_env {
    set +o nounset
    cat << EOF
DST_BUCKET_STACK_NAME:        ${DST_BUCKET_STACK_NAME}
FUNCTION_STACK_NAME:          ${FUNCTION_STACK_NAME}
SCHEDULER_STACK_NAME:         ${SCHEDULER_STACK_NAME}
PERSONAL_BUILD:               ${PERSONAL_BUILD}
BUILD_NUMBER:                 ${BUILD_NUMBER}
EOF
    set -o nounset
}

if [ ${verbose} == true ]; then
    echo "executing deploy using:"
    display_env
fi

export FUNCTION_STACK_NAME=${FUNCTION_STACK_NAME}
export SCHEDULER_STACK_NAME=${SCHEDULER_STACK_NAME}
export DST_BUCKET_STACK_NAME=${DST_BUCKET_STACK_NAME}

echo "deploying INFRASTRUCTURE ..."
if [ ${DEPLOY_INFRASTRUCTURE} == true ]; then
  (cd cfn/; cf sync -y ${DST_BUCKET_STACK_NAME}.yaml)
else
  echo "SKIP deploying infrastructure!"
fi

function set_target_s3_key_for_lambda {
    local version=$(cat target/VERSION)
    local zipfile=$(ls target/ | grep -e '.zip$')
    S3_KEY_FOR_LAMBDA="dist/v${version}/${zipfile}"
}

function write_env_variables_to_disc {
    if [ ! -d "target" ]; then
        mkdir target
    fi
    echo "${FUNCTION_STACK_NAME}"   > target/FUNCTION_STACK_NAME
    echo "${SCHEDULER_STACK_NAME}"  > target/SCHEDULER_STACK_NAME
    echo "${DST_BUCKET_STACK_NAME}" > target/DST_BUCKET_STACK_NAME
}

echo "deploying CODE ..."
if [ ${DEPLOY_CODE} == true ]; then
    set_dst_s3_bucket_name_from_stack
    echo "deploying lambda zip to bucket: ${S3_BUCKET_NAME}"
    extra_opts=''
    [ ${verbose} == true ] && extra_opts='-X'
    pyb ${extra_opts} prepare
    unset_proxy_env
    pyb ${extra_opts} --exclude verify -P bucket_name="${S3_BUCKET_NAME}" upload_zip_to_s3
    restore_proxy_env
    write_env_variables_to_disc

    echo "deploying/update lambda function ..."
    set_target_s3_key_for_lambda
    (cd cfn/; cf sync -y ${FUNCTION_STACK_NAME}.yaml -p ${FUNCTION_STACK_NAME}.s3key=${S3_KEY_FOR_LAMBDA})

    if [ ${PERSONAL_BUILD} == true ]; then
        echo "integration testing ..."
        pyb ${extra_opts} verify -P bucket_name="${S3_BUCKET_NAME}"
        write_env_variables_to_disc
    else
        echo "skipping integration tests, because of PERSONAL_BUILD = false"
        echo "you can manually run the integration tests with: "
        echo "pyb run_integration_tests"
    fi
else
   echo "SKIP deploying Code!"
fi

echo "deploying SCHEDULER ..."
if [ ${DEPLOY_SCHEDULER} == true ]; then
    #set_dst_s3_bucket_name_from_stack
    #set_target_s3_key_for_lambda
    echo "deploying/update scheduler ..."
    (cd cfn/; cf sync -y ${SCHEDULER_STACK_NAME}.yaml)
else
   echo "SKIP deploying SCHEDULER!"
fi


write_env_variables_to_disc
display_env
