from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3 as boto
from moto import mock_s3

from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.s3_utils import list_folders
from rds_log_dog.rds_instance import RDSInstance

class Test(unittest.TestCase):

    @classmethod
    @mock_s3
    def setUpClass(self):
        self.s3 = boto.client('s3')
        self.rds_instance = RDSInstance('rds_id')
        self.s3_dst_bucket_name = 'mybucket'
        self.s3_dst_logs_prefix = 'rds_logs'
        self.dst_full_prefix_for_instance='rds_logs/rds_id'

    def create_dst_bucket(self):
        self.s3.create_bucket(Bucket=self.s3_dst_bucket_name)

    def get_new_logfilehandler(self):
        return LogFileHandler(self.rds_instance, self.s3_dst_bucket_name, self.s3_dst_logs_prefix)

    @mock_s3
    def test_get_s3_dst_prefix(self):
        logfilehandler = self.get_new_logfilehandler()
        self.assertEqual(self.dst_full_prefix_for_instance, logfilehandler.get_s3_dst_prefix())
    
    @mock_s3
    def test_setup_s3_destination_with_existing(self):
        self.create_dst_bucket()
        self.s3.put_object(Bucket=self.s3_dst_bucket_name, Key='{}/'.format(self.s3_dst_logs_prefix))
        logfilehandler = self.get_new_logfilehandler()
        logfilehandler.setup_s3_destination()
        folders = list_folders(
                Bucket=self.s3_dst_bucket_name, Prefix=self.s3_dst_logs_prefix) 
        # foldername is rds_instance id (see test_get_s3_dst_prefix())
        self.assertTrue({self.rds_instance.get_id()}.issubset(folders))
    
    @mock_s3
    def test_setup_s3_destination_on_empty_bucket(self):
        self.create_dst_bucket()
        logfilehandler = self.get_new_logfilehandler()
        logfilehandler.setup_s3_destination()
        folders = list_folders(
                Bucket=self.s3_dst_bucket_name, Prefix=self.s3_dst_logs_prefix) 
        self.assertTrue({self.rds_instance.get_id()}.issubset(folders))

    @mock_s3
    def test_discover_s3_logfiles(self):
        self.create_dst_bucket()
        logfiles={'log1','log2'}
        for file in logfiles:
            self.s3.put_object(Bucket=self.s3_dst_bucket_name, Key='{}/{}'.format(self.dst_full_prefix_for_instance, file))
        logfilehandler = self.get_new_logfilehandler()
        self.assertEqual(logfiles, logfilehandler.discover_s3_logfiles())

if __name__ == '__main__':
    unittest.main()

