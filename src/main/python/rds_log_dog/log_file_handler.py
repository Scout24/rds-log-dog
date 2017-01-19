from __future__ import print_function, absolute_import, unicode_literals, division

import boto3
from .rds_instance import RDSInstance
from .log_file import LogFile

logger = logging.getLogger(__name__)

class LogFileHandler(object):

    def __init__(self, rds_instance, s3_dst_bucket, s3_dst_prefix):
        self.rds_instance = rds_instance
        self.dst_bucket = s3_dst_bucket
        self.dst_prefix_all = s3_dst_prefix
        # prefix for rds logs of the given instance
        self.dst_prefix_instance = self.get_s3_dst_prefix_for_instance()

    def setup_s3_destination(self):
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(
            Bucket=self.dst_bucket, Prefix=self.dst_prefix_instance)
        if 'Contents' not in response:
            s3.put_object(
                Bucket=self.dst_bucket, Key='{}/'.format(self.dst_prefix_instance))
            logger.debug('created missing s3 dest: {}'.format(
                self.dst_prefix_instance))

    def get_s3_dst_prefix_for_instance(self):
        return "{}/{}".format(self.dst_prefix_all, self.rds_instance.name)

    def s3_get_objects(self, bucket, prefix):
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(
            Bucket=bucket, Prefix=prefix)
        if 'Contents' in response:
            return response['Contents']
        return None

    def discover_s3_logfiles(self):
        files = set()
        for file in self.s3_get_objects(self.dst_bucket, self.dst_prefix_instance):
            if len(file['Key']) > len(self.dst_prefix_instance) + 1:
                log_file = LogFile(
                    file['Key'][len(self.dst_prefix_instance) + 1:])
                files.add(log_file)
        return files

    def rds_logfiles(self, name):
        client = boto3.client('rds')
        response = client.describe_db_log_files(
            DBInstanceIdentifier=name)
        if 'DescribeDBLogFiles' in response:
            return response['DescribeDBLogFiles']
        return set()

    def discover_rds_logfiles(self):
        return { LogFile(e['LogFileName']) for e in self.rds_logfiles(self.rds_instance.name) }

