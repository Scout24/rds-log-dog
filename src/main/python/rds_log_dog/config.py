from __future__ import print_function, absolute_import, division
import logging


class Config(object):

    def __init__(self, s3_bucket, prefix='rds_logs'):
        logger = logging.getLogger(__name__)
        self.s3_dst_bucket = s3_bucket
        self.s3_prefix_for_logs = prefix
        logger.debug('s3 dst bucket: %s', self.s3_dst_bucket)
        logger.debug('s3 dst prefix: %s', self.s3_prefix_for_logs)
