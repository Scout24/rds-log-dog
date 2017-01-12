#!/usr/bin/env bash

# ------------------- config 
S3_PREFIX_FOR_RDS_LOGS=rds_logs

source helper.sh
source ../../helper.sh

#set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

function exit_msg {
    echo "[ERROR] $1"
    exit 1
}

# 0. pre: lambda invoked
# s3 dst path exists
set_templates_and_stack_names
set_dst_s3_bucket_name_from_stack

COUNT=$(aws s3 ls ${S3_BUCKET_NAME} | grep -c "PRE ${S3_PREFIX_FOR_RDS_LOGS}/")
if [ "${COUNT}" != "1" ]; then
    exit_msg "path not found in ${S3_BUCKET_NAME}"
fi
# # of prefixes in s3
# discover how many rds instances exists
# compare s3 with rds instances  

echo "[OK]"
