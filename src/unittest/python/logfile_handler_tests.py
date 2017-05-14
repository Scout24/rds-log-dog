from __future__ import print_function, absolute_import, division

import unittest2 as unittest
import boto3
import logging
from tempfile import NamedTemporaryFile
from moto import mock_s3
from mock import patch

from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.s3_utils import list_folders, setup_s3_destination
from rds_log_dog.rds_instance import RDSInstance
from rds_log_dog.log_file import S3LogFile, RdsLogFile, LogFile


class Test(unittest.TestCase):

    @classmethod
    @mock_s3
    def setUpClass(self):
        self.s3 = boto3.client('s3')
        self.rds_instance = RDSInstance('rds_id')

    @mock_s3
    def test_get_s3_dst_prefix(self):
        logfilehandler = LogFileHandler(
            self.rds_instance, 'bucket', 'logs_prefix')
        self.assertEqual('logs_prefix/{}'.format(self.rds_instance.name),
                         logfilehandler.get_s3_dst_prefix_for_instance())

    @mock_s3
    def test_setup_s3_destination_with_existing(self):
        self.s3.create_bucket(Bucket='bucket')
        self.s3.put_object(Bucket='bucket', Key='logs_prefix/')
        logfilehandler = LogFileHandler(
            self.rds_instance, 'bucket', 'logs_prefix')
        setup_s3_destination(logfilehandler.dst_bucket,
                             logfilehandler.dst_prefix_instance)
        folders = list_folders(bucket='bucket', prefix='logs_prefix')
        # foldername is rds_instance id (see test_get_s3_dst_prefix())
        self.assertTrue({self.rds_instance.name}.issubset(folders))

    @mock_s3
    def test_setup_s3_destination_on_empty_bucket(self):
        self.s3.create_bucket(Bucket='bucket')
        logfilehandler = LogFileHandler(
            self.rds_instance, 'bucket', 'logs_prefix')
        setup_s3_destination(logfilehandler.dst_bucket,
                             logfilehandler.dst_prefix_instance)
        folders = list_folders(bucket='bucket', prefix='logs_prefix')
        self.assertTrue({self.rds_instance.name}.issubset(folders))

    @mock_s3
    def test_discover_logfiles_in_s3(self):
        # bucket must exist
        self.s3.create_bucket(Bucket='bucket')

        self.s3.put_object(Bucket='bucket', Key='logs/inst1/f1')
        self.s3.put_object(Bucket='bucket', Key='logs/inst1/f2')
        # now some logfile for another instance
        self.s3.put_object(Bucket='bucket', Key='logs/other/f1')

        logfiles = {S3LogFile('f1', '', '', size=0),
                    S3LogFile('f2', '', '', size=0)}
        logfilehandler = LogFileHandler(RDSInstance('inst1'), 'bucket', 'logs')
        self.assertSetEqual(logfiles, logfilehandler.discover_logfiles_in_s3())

    @mock_s3
    def test_discover_s3_logfiles_with_no_logfiles(self):
        # bucket must exist
        self.s3.create_bucket(Bucket='bucket')

        logfilehandler = LogFileHandler(
            self.rds_instance, 'bucket', 'logs_prefix')
        # destination for logfiles must exist, so create it
        setup_s3_destination(logfilehandler.dst_bucket,
                             logfilehandler.dst_prefix_instance)
        self.assertEqual(set(), logfilehandler.discover_logfiles_in_s3())

    @patch('rds_log_dog.rds_utils.describe_logfiles_of_instance')
    def test_discover_rds_logfiles_with_no_logfiles(self, describe_logfiles_of_instance):
        # emulate response of AWS api call part DescribeDBLogFiles
        describe_logfiles_of_instance.return_value = []
        logfilehandler = LogFileHandler(self.rds_instance, 'foo', 'bar')
        result = logfilehandler.discover_logfiles_in_rds()
        describe_logfiles_of_instance.assert_called_with(
            self.rds_instance.name)
        self.assertEqual(set(), result)

    @patch('rds_log_dog.rds_utils.describe_logfiles_of_instance')
    def test_discover_rds_logfiles(self, describe_logfiles_of_instance):
        # emulate response of AWS api call part DescribeDBLogFiles
        describe_logfiles_of_instance.return_value = [
            {'LogFileName': 'file1', 'LastWritten': 123, 'Size': 124},
            {'LogFileName': 'file2', 'LastWritten': 123, 'Size': 124}
        ]
        logfilehandler = LogFileHandler(self.rds_instance, 'foo', 'bar')
        result = logfilehandler.discover_logfiles_in_rds()
        describe_logfiles_of_instance.assert_called_with(
            self.rds_instance.name)
        self.assertEqual(
            {RdsLogFile('file1', '', size=124),
             RdsLogFile('file2', '', size=124)},
            result)

    def test_logfiles_to_copy_empty_src(self):
        src = set()
        dst = set()
        self.assertEqual(set(), LogFileHandler.logfiles_to_copy(src, dst))
        dst = {S3LogFile('foo', '', '')}
        self.assertEqual(set(), LogFileHandler.logfiles_to_copy(src, dst))

    def test_logfiles_to_copy_empty_dst(self):
        dst = set()
        src = {RdsLogFile('foo', '')}
        self.assertEqual(src, LogFileHandler.logfiles_to_copy(src, dst))
        src = {RdsLogFile('foo', ''), RdsLogFile('bar', '')}
        self.assertEqual(src, LogFileHandler.logfiles_to_copy(src, dst))

    def test_logfiles_to_copy_new_files_on_src(self):
        src = {RdsLogFile('foo', ''), RdsLogFile('bar', '')}
        dst = {S3LogFile('foo', '', '')}
        self.assertEqual({LogFile('bar')},
                         LogFileHandler.logfiles_to_copy(src, dst))

    def test_logfiles_to_copy_new_files_on_src_old_on_dst(self):
        src = {RdsLogFile('foo', ''), RdsLogFile('bar', '')}
        dst = {S3LogFile('foo', '', ''), S3LogFile('xyz', '', '')}
        self.assertEqual({LogFile('bar')},
                         LogFileHandler.logfiles_to_copy(src, dst))

    def test_logfiles_to_copy_size_diff(self):
        src = {RdsLogFile('foo', '', size=123)}
        dst = {S3LogFile('foo', '', '', size=0)}
        self.assertEqual({LogFile('foo', size=123)},
                         LogFileHandler.logfiles_to_copy(src, dst))


if __name__ == '__main__':
    unittest.main()
