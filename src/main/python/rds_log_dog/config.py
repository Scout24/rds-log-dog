import logging

logger = logging.getLogger(__name__)


class Config(object):

    def __init__(self, s3_bucket):
        self.s3_dst_bucket = s3_bucket
        self.s3_prefix_for_logs = 'rds_logs'
        logger.debug('s3 dst bucket: {}'.format(self.s3_dst_bucket))
        logger.debug('s3 dst prefix: {}'.format(self.s3_prefix_for_logs))
