from __future__ import unicode_literals

import boto3


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

    def write(self, data):
        assert (self.bucket and self.prefix), "call set_s3_dst() first, before write"
        client = boto3.client('s3')
        client.put_object(
            Bucket=self.bucket,
            Key=self.get_s3_dst_key(),
            Body=data)

    def read_from_rds(self):
        assert (self.rds_name), "call set_rds_src() first, before reading from rds"
        client = boto3.client('rds')
        marker = '0'
        data = ''
        while True:
            response = client.download_db_log_file_portion(
                DBInstanceIdentifier=self.rds_name,
                LogFileName=self.name, Marker=marker)
            data += response['LogFileData']
            if not response['AdditionalDataPending']:
                break
            marker = response['Marker']
        return data

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
