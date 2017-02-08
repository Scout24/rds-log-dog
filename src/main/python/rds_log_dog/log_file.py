from __future__ import unicode_literals

import rds_utils as rds
import s3_utils as s3


class LogFile(object):

    def __init__(self, name):
        self.name = name
        self.size = None

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "[<LogFile|{}> :: name: {}, size: {}]".format(type(self), self.name, self.size)

    def __eq__(self, other):
        if isinstance(other, LogFile):
            return (self.name == other.name) and (self.size == other.size)
        return False

    def __ne__(self, other):
        return not self == other


class s3LogFile(LogFile):

    def __init__(self, name, bucket, prefix):
        LogFile.__init__(self, name)
        self.bucket = bucket
        self.prefix = prefix

    def get_dst_key(self):
        return '{}/{}'.format(self.prefix, self.name)

    def fetch_size(self):
        self.size = s3.get_size(self.bucket, self.get_dst_key())

    def write(self, data):
        s3.write_data_to_object(self.bucket, self.get_dst_key(), data)

class rdsLogFile(LogFile):

    def __init__(self, name, instance_name):
        LogFile.__init__(self, name)
        self.instance_name = instance_name

    def fetch_size(self):
        self.size = rds.get_size(self.instance_name, self.name)

    def read(self):
        return rds.get_full_db_logfile_data(self.instance_name, self.name)
