from __future__ import print_function, absolute_import, division

import subprocess
import os
from subprocess import Popen, PIPE
from rds_log_dog.cfn_utils import cfn_get_output


def get_env():
    function_stack_name = os.getenv('FUNCTION_STACK_NAME', None)
    if not function_stack_name:
        with open('target/FUNCTION_STACK_NAME', 'r') as f:
            function_stack_name = f.read().strip()

    bucket_stack_name = os.getenv('DST_BUCKET_STACK_NAME', None)
    if not bucket_stack_name:
        with open('target/DST_BUCKET_STACK_NAME', 'r') as f:
            bucket_stack_name = f.read().strip()

    lambda_function_name = cfn_get_output(function_stack_name, 'lambdaFunctionName')
    bucket_name = cfn_get_output(bucket_stack_name, 'name')
    return (function_stack_name, bucket_stack_name, lambda_function_name, bucket_name)


def execute_command(cmd, timeout=None):
    if timeout:
        cmd = 'timeout {0} {1}'.format(timeout, cmd)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return (p.returncode, stdout, stderr)


def do():
    cmd = "aws s3 ls"
    rc, stdout, stderr = execute_command(cmd)

    type(stdout)
    print("rc: ", rc)
    print("output: ", stdout)
    print("error: ", stderr)
    print("--")

if __name__ == "__main__":
    do()
