#!/usr/bin/env bash

#
# execute integration tests (bash)
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

function failed {
    if [ $? == 0 ]; then
        txt="\033[0;32m Integration Tests successful \033[0m";
    else
        txt="\033[0;31m Integration Tests failed \033[0m";
    fi
    echo "-----------------------------------------"
    echo -e $txt
    echo "-----------------------------------------"
    echo
}

trap failed EXIT
echo "[INFO] executing (bash based) tests in src/integrationtest/ ..."
for file in $(ls src/integrationtest/*_tests.sh); do
    echo "[INFO] run $file ..."
    $file
done

