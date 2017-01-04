#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

./deploy_infrastructure.sh
# TODO: pyb deploy lambda

