#!/usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals, division
from rds_log_dog.rds_log_dog import RDSLogDog

def lambda_handler(event, context):
    m = RDSLogDog()
    return m.do()

if __name__ == "__main__":
     print("local mode executing ...")
     m = RDSLogDog()
     m.do()

