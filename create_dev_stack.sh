#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

source helper.sh

PERSONAL_BUILD=false
set_templates_and_stack_names
BASE_DST_BUCKET_STACK_NAME=${DST_BUCKET_STACK_NAME}
BASE_FUNCTION_STACK_NAME=${FUNCTION_STACK_NAME}

PERSONAL_BUILD=true
set_templates_and_stack_names

cd cfn/

cp ${BASE_DST_BUCKET_STACK_NAME}.yaml ${DST_BUCKET_STACK_NAME}.yaml
sed -i "s/^\(\s*\)${BASE_DST_BUCKET_STACK_NAME}:/\1${DST_BUCKET_STACK_NAME}:/" ${DST_BUCKET_STACK_NAME}.yaml

cp ${BASE_FUNCTION_STACK_NAME}.yaml ${FUNCTION_STACK_NAME}.yaml
sed -i "s/^\(\s*\)${BASE_FUNCTION_STACK_NAME}:/\1${FUNCTION_STACK_NAME}:/" ${FUNCTION_STACK_NAME}.yaml
sed -i "s/\(\|ref\|\)${BASE_DST_BUCKET_STACK_NAME}\./\1${DST_BUCKET_STACK_NAME}./" ${FUNCTION_STACK_NAME}.yaml

# set gitignore
touch .gitignore
grep -q "${DST_BUCKET_STACK_NAME}.yaml" ".gitignore" || echo "${DST_BUCKET_STACK_NAME}.yaml" >> .gitignore
grep -q "${FUNCTION_STACK_NAME}.yaml" ".gitignore" || echo "${FUNCTION_STACK_NAME}.yaml" >> .gitignore

echo "created new stack definitions from orginal ones:"
echo "${DST_BUCKET_STACK_NAME}.yaml"
echo "${FUNCTION_STACK_NAME}.yaml"

