from __future__ import unicode_literals

import rds_utils as rds
import s3_utils as s3

class LogFile(object):

    def __init__(self, name):
        self.name = name
        self.bucket = None
        self.prefix = None
        self.rds_name = None

    def set_s3_dst(self, bucket, prefix):
        self.bucket = bucket
        self.prefix = prefix

    def set_rds_src(self, name):
        self.rds_name = name

    def get_s3_dst_key(self):
        return '{}/{}'.format(self.prefix, self.name)

    def ensure_logfile_is_s3_logfile(self):
        assert (self.bucket and self.prefix), "call set_s3_dst() first, before write"

    def write_data(self, data):
        self.ensure_logfile_is_s3_logfile()
        s3.write_data_to_object(self.bucket, self.get_s3_dst_key(), data)

    def ensure_logfile_is_rds_logfile(self):
        assert (self.rds_name), "call set_rds_src() first, before reading from rds"

    def read_data(self):
        self.ensure_logfile_is_rds_logfile()
        return rds.get_full_db_logfile_data(self.rds_name, self.name)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "LogFile name: {}".format(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    def __ne__(self, other):
        return not self == other
