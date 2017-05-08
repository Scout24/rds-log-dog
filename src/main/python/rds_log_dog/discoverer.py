from __future__ import print_function, absolute_import, division

import boto3

from rds_log_dog.rds_instance import RDSInstance


class Discoverer(object):

    @staticmethod
    def discover():
        client = boto3.client('rds')
        response = client.describe_db_instances()
        return [RDSInstance(i['DBInstanceIdentifier']) for i in response['DBInstances']]
