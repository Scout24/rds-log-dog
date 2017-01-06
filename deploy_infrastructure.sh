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

# check preconditions
command -v cf >/dev/null 2>&1 || { echo >&2 "I require cfn-sphere but it's not installed. Install with: pip install cfn-sphere. Aborting."; exit 1; }

# sync the with AWS
cf sync ${stackfile} -y

