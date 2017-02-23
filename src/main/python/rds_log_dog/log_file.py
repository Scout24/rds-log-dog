from __future__ import print_function, absolute_import, unicode_literals, division

import rds_log_dog.rds_utils as rds
import rds_log_dog.s3_utils as s3


class LogFile(object):

    def __init__(self, name, size=None):
        self.name = name
        self.size = size

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


class S3LogFile(LogFile):

    def __init__(self, name, bucket, prefix, size=None):
        LogFile.__init__(self, name, size)
        self.bucket = bucket
        self.prefix = prefix

    def get_dst_key(self):
        return '{}/{}'.format(self.prefix, self.name)

    def fetch_size(self):
        self.size = s3.get_size(self.bucket, self.get_dst_key())
        return self.size

    def write(self, fileobj):
        s3.copy(self.bucket, self.get_dst_key(), fileobj)


class RdsLogFile(LogFile):

    def __init__(self, name, instance_name, size=None):
        LogFile.__init__(self, name, size)
        self.instance_name = instance_name

    def fetch_size(self):
        self.size = rds.get_size(self.instance_name, self.name)
        return self.size

    def download(self, file_handle):
        return rds.download(self.instance_name, self.name, file_handle)

