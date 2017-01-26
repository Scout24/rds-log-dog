from __future__ import print_function, absolute_import, unicode_literals, division

import boto3

from rds_log_dog.discoverer import Discoverer
from rds_log_dog.cfn_utils import cfn_get_output


def get_one_rds_instance():
    disco = Discoverer()
    instances = disco.discover()
    assert (0 < len(instances)), "We need at least one RDS instance for this test!"
    # pick one instance
    return instances.pop()


def get_lambda_function_name():
    with open('target/FUNCTION_STACK_NAME', 'r') as f:
        function_stack_name = f.read().strip()
    return cfn_get_output(function_stack_name, 'name')


def invoke_lambda():
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=get_lambda_function_name(), LogType='Tail')
    return response
