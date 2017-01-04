#!/usr/bin/env bash

# 
# Deploy cloudformation based stack
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

stackfile="${1:-rds-log-dog.yaml}"

echo "using ${stackfile} ..."

# Set magic variables for current file & dir
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename ${__file} .sh)"

# the temp directory used, within $DIR
TMP_DIR=`mktemp -d -p "${__dir}"`
# link the templates there
ln -s ${__dir}/cfn/templates ${TMP_DIR}/

# deletes the temp directory
function cleanup {
    rm -rf "${TMP_DIR}"
    #echo "Deleted temp working directory ${TMP_DIR}"
}

# register the cleanup function to be called on the EXIT signal
trap cleanup EXIT

# check preconditions
command -v cf >/dev/null 2>&1 || { echo >&2 "I require cfn-sphere but it's not installed. Install with: pip install cfn-sphere. Aborting."; exit 1; }

# substitute some VARs in the stack template
eval "cat <<EOF
$(<cfn/${stackfile})
EOF
" 2> /dev/null >${TMP_DIR}/${stackfile}

# sync the with AWS
cf sync ${TMP_DIR}/${stackfile} -y


