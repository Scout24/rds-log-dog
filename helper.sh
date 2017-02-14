# source this file only

function set_templates_and_stack_names {
   local BASENAME=rds-log-dog
   local POSTFIX=""
   if [ ${PERSONAL_BUILD} == true ]; then
      POSTFIX="-${USER:0:3}"
   fi
   DST_BUCKET_STACK_NAME="${BASENAME}-s3${POSTFIX}"
   FUNCTION_STACK_NAME="${BASENAME}-lambda${POSTFIX}"
   SCHEDULER_STACK_NAME="${BASENAME}-scheduler${POSTFIX}"
}

function set_dst_s3_bucket_name_from_stack {
    S3_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${DST_BUCKET_STACK_NAME} | jq -r '.[]|.[].Outputs|.[]|select(.OutputKey=="name")|.OutputValue')
}

function unset_proxy_env {
    set +o nounset
    unset __HTTP_PROXY
    unset __HTTPS_PROXY
    [ -n "$http_proxy" ]   && export __HTTP_PROXY=$http_proxy && unset http_proxy
    [ -n "$HTTP_PROXY" ]   && export __HTTP_PROXY=$HTTP_PROXY && unset HTTP_PROXY
    [ -n "$https_proxy" ]  && export __HTTPS_PROXY=$https_proxy && unset https_proxy
    [ -n "$HTTPS_PROXY" ]  && export __HTTPS_PROXY=$HTTPS_PROXY && unset HTTPS_PROXY
    set -o nounset
}

function restore_proxy_env {
    set +o nounset
    [ -n "$__HTTP_PROXY" ] && export HTTP_PROXY=$__HTTP_PROXY && unset __HTTP_PROXY
    [ -n "$__HTTPS_PROXY" ] && export HTTPS_PROXY=$__HTTPS_PROXY && unset __HTTPS_PROXY
    set -o nounset
}

function print_section {
    printf '%.s*' {1..80} 1>&2; echo 1>&2;
    echo "**** $1 " 1>&2
    printf '%.s*' {1..80} 1>&2; echo 1>&2;
}
