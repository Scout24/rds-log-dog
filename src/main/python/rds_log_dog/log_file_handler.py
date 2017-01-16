from __future__ import print_function, absolute_import, unicode_literals, division

import boto3
from .rds_instance import RDSInstance
from .config import get_logger

class LogFileHandler(object):

    def __init__(self, rds_instance, s3_dst_bucket, s3_dst_prefix):
       self.rds_instance = rds_instance
       self.dst_bucket = s3_dst_bucket
       self.dst_prefix = s3_dst_prefix
       self.logger = get_logger(__name__)

    def setup_s3_destination(self):
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=self.dst_bucket, Prefix=self.get_s3_dst_prefix())
        if 'Contents' not in response:
            s3.put_object(
                    Bucket=self.dst_bucket, Key='{}/'.format(self.get_s3_dst_prefix()))
            self.logger.debug('created missing s3 dest: {}'.format(self.get_s3_dst_prefix()))

    def get_s3_dst_prefix(self):
        return "{}/{}".format(self.dst_prefix, self.rds_instance.get_id())

