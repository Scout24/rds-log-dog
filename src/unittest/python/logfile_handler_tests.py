from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
from moto import mock_s3
from mock import patch

from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.s3_utils import list_folders
from rds_log_dog.rds_instance import RDSInstance
from rds_log_dog.log_file import LogFile


class Test(unittest.TestCase):

    @classmethod
    @mock_s3
    def setUpClass(self):
        self.s3 = boto3.client('s3')
        self.rds_instance = RDSInstance('rds_id')
        self.s3_dst_bucket_name = 'mybucket'
        self.s3_dst_logs_prefix = 'rds_logs'
        self.dst_full_prefix_for_instance = 'rds_logs/rds_id'

    def create_dst_bucket(self):
        self.s3.create_bucket(Bucket=self.s3_dst_bucket_name)

    def get_new_logfilehandler(self):
        return LogFileHandler(self.rds_instance, self.s3_dst_bucket_name, self.s3_dst_logs_prefix)

    @mock_s3
    def test_get_s3_dst_prefix(self):
        logfilehandler = self.get_new_logfilehandler()
        self.assertEqual(self.dst_full_prefix_for_instance,
                         logfilehandler.get_s3_dst_prefix_for_instance())

    @mock_s3
    def test_setup_s3_destination_with_existing(self):
        self.create_dst_bucket()
        self.s3.put_object(Bucket=self.s3_dst_bucket_name,
                           Key='{}/'.format(self.s3_dst_logs_prefix))
        logfilehandler = self.get_new_logfilehandler()
        logfilehandler.setup_s3_destination()
        folders = list_folders(
            Bucket=self.s3_dst_bucket_name, Prefix=self.s3_dst_logs_prefix)
        # foldername is rds_instance id (see test_get_s3_dst_prefix())
        self.assertTrue({self.rds_instance.name}.issubset(folders))

    @mock_s3
    def test_setup_s3_destination_on_empty_bucket(self):
        self.create_dst_bucket()
        logfilehandler = self.get_new_logfilehandler()
        logfilehandler.setup_s3_destination()
        folders = list_folders(
            Bucket=self.s3_dst_bucket_name, Prefix=self.s3_dst_logs_prefix)
        self.assertTrue({self.rds_instance.name}.issubset(folders))

    @mock_s3
    def test_discover_s3_logfiles(self):
        # bucket must exist
        self.create_dst_bucket()
        logfiles = {LogFile('log1'), LogFile('log2')}
        for file in logfiles:
            self.s3.put_object(Bucket=self.s3_dst_bucket_name,
                               Key='{}/{}'.format(self.dst_full_prefix_for_instance, file.name))
        # now some logfile for another instance
        self.s3.put_object(Bucket=self.s3_dst_bucket_name,
                           Key='{}/otherrds/{}'.format(self.s3_dst_logs_prefix, 'logA'))
        logfilehandler = self.get_new_logfilehandler()
        #import pdb; pdb.set_trace()
        self.assertSetEqual(logfiles, logfilehandler.discover_s3_logfiles())

    @mock_s3
    def test_discover_s3_logfiles_with_no_logfiles(self):
        # bucket must exist
        self.create_dst_bucket()
        logfilehandler = self.get_new_logfilehandler()
        # destination for logfiles must exist, so create it
        logfilehandler.setup_s3_destination()
        self.assertEqual(set(), logfilehandler.discover_s3_logfiles())

    @patch('rds_log_dog.log_file_handler.LogFileHandler.rds_logfiles')
    def test_discover_rds_logfiles(self, rds_logfiles):
        rds_logfiles.return_value = [
            {'LogFileName': 'file1'},
            {'LogFileName': 'file2'}
        ]
        logfilehandler = self.get_new_logfilehandler()
        self.assertItemsEqual({LogFile('file1'), LogFile(
            'file2')}, logfilehandler.discover_rds_logfiles())

    @patch('rds_log_dog.log_file_handler.LogFileHandler.rds_logfiles')
    def test_discover_rds_logfiles_with_no_logfiles(self, rds_logfiles):
        rds_logfiles.return_value = set()
        logfilehandler = self.get_new_logfilehandler()
        self.assertItemsEqual(set(), logfilehandler.discover_rds_logfiles())

    def test_new_logfiles_empty_src(self):
        src = set()
        dst = set()
        self.assertEqual(set(), LogFileHandler.new_logfiles(src, dst))
        dst = {LogFile('foo')}
        self.assertEqual(set(), LogFileHandler.new_logfiles(src, dst))

    def test_new_logfiles_empty_dst(self):
        dst = set()
        src = {LogFile('foo')}
        self.assertEqual({LogFile('foo')},
                         LogFileHandler.new_logfiles(src, dst))
        src = {LogFile('foo'), LogFile('bar')}
        self.assertEqual({LogFile('foo'), LogFile('bar')},
                         LogFileHandler.new_logfiles(src, dst))

    def test_new_logfiles_new_files_on_src(self):
        src = {LogFile('foo'), LogFile('bar')}
        dst = {LogFile('foo')}
        self.assertEqual({LogFile('bar')},
                         LogFileHandler.new_logfiles(src, dst))

    def test_new_logfiles_new_files_on_src_old_on_dst(self):
        src = {LogFile('foo'), LogFile('bar')}
        dst = {LogFile('foo'), LogFile('xyz')}
        self.assertEqual({LogFile('bar')},
                         LogFileHandler.new_logfiles(src, dst))


if __name__ == '__main__':
    unittest.main()
