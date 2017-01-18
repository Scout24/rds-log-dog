#!/usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from rds_log_dog.rds_log_dog import RDSLogDog
from rds_log_dog.config import Config
from rds_log_dog.cfn_utils import cfn_get_output 


def lambda_handler(event, context):
    config = Config(os.environ['dstBucket'])
    m = RDSLogDog(config)
    return m.do()

if __name__ == "__main__":
    print("local mode executing ...")
    bucket_stack_name = os.getenv('DST_BUCKET_STACK_NAME', None)
    if not bucket_stack_name:
        with open('target/DST_BUCKET_STACK_NAME', 'r') as f:
            bucket_stack_name = f.read().strip()
    dst_bucket = cfn_get_output(bucket_stack_name, 'name') 
    os.environ['dstBucket'] = dst_bucket
    lambda_handler(None, None)

