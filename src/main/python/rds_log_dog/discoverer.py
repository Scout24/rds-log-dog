from __future__ import print_function, absolute_import, unicode_literals, division

import boto3
from .rds_instance import RDSInstance
from .config import get_logger

class Discoverer(object):

    def __init__(self, aws_region_name):
       self.aws_region_name = aws_region_name
       self.logger = get_logger(__name__)

    def discover(self):
        client = boto3.client('rds', region_name = self.aws_region_name)
        response = client.describe_db_instances()
        dbinstances = set()
        for instance in response['DBInstances']:
            dbinstance = RDSInstance(instance['DBInstanceIdentifier'])
            dbinstances.add(dbinstance)
            #print('DBInstanceIdentifier: ' + instance['DBInstanceIdentifier'] + '  DBName: ' + instance['DBName'] + '  Engine: ' + instance['Engine'])
        return(dbinstances)
