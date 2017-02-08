from __future__ import print_function, absolute_import, unicode_literals, division

import logging

import rds_log_dog.s3_utils as s3
import rds_log_dog.rds_utils as rds
from .log_file import LogFile, s3LogFile, rdsLogFile

logger = logging.getLogger(__name__)


class LogFileHandler(object):

    def __init__(self, rds_instance, s3_dst_bucket, s3_dst_prefix):
        self.rds_instance = rds_instance
        self.dst_bucket = s3_dst_bucket
        self.dst_prefix_all = s3_dst_prefix
        # full prefix for rds logs of the given instance
        self.dst_prefix_instance = self.get_s3_dst_prefix_for_instance()

    @staticmethod
    def new_logfiles(logfiles_in_src, logfiles_in_dst):
        return logfiles_in_src - logfiles_in_dst

    def get_s3_dst_prefix_for_instance(self):
        return "{}/{}".format(self.dst_prefix_all, self.rds_instance.name)

    def discover_logfiles_in_s3(self):
        files = set()
        for filename in s3.get_files(self.dst_bucket, self.dst_prefix_instance):
            if len(filename) > len(self.dst_prefix_instance) + 1:
                name = filename[len(self.dst_prefix_instance) + 1:]
                log_file = s3LogFile(name, self.dst_bucket, self.dst_prefix_instance)
                files.add(log_file)
        return files

    def discover_logfiles_in_rds(self):
        return {rdsLogFile(e['LogFileName'], self.rds_instance.name) for e in rds.describe_logfiles_of_instance(self.rds_instance.name)}

    def copy(self, src):
        s3LogFile(src.name, self.dst_bucket, self.dst_prefix_instance).write(src.read())
