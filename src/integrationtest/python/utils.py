from __future__ import print_function, absolute_import, unicode_literals, division

import boto3
import random
import uuid
import logging 

from rds_log_dog.discoverer import Discoverer
from rds_log_dog.cfn_utils import cfn_get_output
import rds_log_dog.rds_utils as rds

logger = logging.getLogger('ittest')


def get_one_rds_instance():
    disco = Discoverer()
    instances = disco.discover()
    assert (0 < len(instances)), "We need at least one RDS instance for this test!"
    # pick one instance
    return instances.pop()


def get_lambda_function_name():
    with open('target/FUNCTION_STACK_NAME', 'r') as f:
        function_stack_name = f.read().strip()
    return cfn_get_output(function_stack_name, 'lambdaFunctionName')


def invoke_lambda():
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=get_lambda_function_name(), LogType='Tail')
    return response


def file_exists_in_s3(bucket, key):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket)
    match = [o['Key'] for o in response['Contents'] if o['Key'] == key]
    return len(match) > 0


def get_one_random_logfile(instance_name):
    logfiles = rds.describe_logfiles_of_instance(instance_name)
    return logfiles[random.choice(range(0, len(logfiles) - 1))]['LogFileName']


def get_temp_prefix():
    return "ittests/{}".format(uuid.uuid4())


def delete_prefix(bucket, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    keys_to_delete = {'Objects': []}
    keys_to_delete['Objects'] = [{'Key': o['Key']} for o in response['Contents']]
    response = s3.delete_objects(Bucket=bucket, Delete=keys_to_delete)


def choose_one_random_logfile_does_not_exists_in_s3(rds_instance_name, bucket):
    max_retries = 10
    while max_retries > 0:
        max_retries -= 1
        logfile = get_one_random_logfile(rds_instance_name)
        if not file_exists_in_s3(bucket, logfile):
            return logfile
    logger.error('chosing one random new logfile to download failed 10 times!')
