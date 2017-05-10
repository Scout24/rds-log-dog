from __future__ import print_function, absolute_import, division

from tempfile import NamedTemporaryFile
import unittest2 as unittest
from mock import patch

from rds_log_dog.log_file import S3LogFile, RdsLogFile


class Test(unittest.TestCase):

    def test_s3_log_file_init(self):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        self.assertEqual('foo', log_file.name)
        self.assertEqual('prefix', log_file.prefix)
        self.assertEqual('bucket', log_file.bucket)

    def test_rds_log_file_init(self):
        rds_log = RdsLogFile('foo', 'instance')
        self.assertEqual('foo', rds_log.name)
        self.assertEqual('instance', rds_log.instance_name)

    @patch('rds_log_dog.rds_utils.download')
    def test_rds_download(self, download):
        rds_log = RdsLogFile('foofile', 'instance')
        with NamedTemporaryFile() as tempfile:
            rds_log.download(tempfile)
            download.assert_called_with('instance', 'foofile', tempfile)

    @patch('rds_log_dog.s3_utils.copy')
    def test_s3_write(self, copy):
        log_file = S3LogFile('name', 'bucket', 'prefix')
        with NamedTemporaryFile() as tempfile:
            log_file.write(tempfile)
            copy.assert_called_with('bucket', 'prefix/name', tempfile)

    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size_s3(self, get_size):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        get_size.return_value = 23
        log_file.fetch_size()
        get_size.assert_called_with('bucket', log_file.get_dst_key())
        self.assertEqual(23, log_file.size)

    @patch('rds_log_dog.rds_utils.get_size')
    def test_fetch_size_rds(self, get_size):
        rds_log = RdsLogFile('foo', 'instance')
        get_size.return_value = 23
        rds_log.fetch_size()
        get_size.assert_called_with('instance', 'foo')
        self.assertEqual(23, rds_log.size)

    @patch('rds_log_dog.rds_utils.get_size')
    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size_s3__calls(self, s3_get_size, rds_get_size):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        log_file.fetch_size()
        self.assertTrue(s3_get_size.called)
        self.assertFalse(rds_get_size.called)

    @patch('rds_log_dog.rds_utils.get_size')
    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size_rds__calls(self, s3_get_size, rds_get_size):
        rds = RdsLogFile('foo', 'instance')
        rds.fetch_size()
        self.assertFalse(s3_get_size.called)
        self.assertTrue(rds_get_size.called)

    def test_get_dst_key(self):
        log_file = S3LogFile('name', 'bucket', 'prefix')
        self.assertEqual('prefix/name', log_file.get_dst_key())

    def test_equals__wo_size(self):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        rds_file = RdsLogFile('foo', 'instance')
        self.assertEqual(log_file, rds_file)

    def test_not_equals__wo_size(self):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        rds_file = RdsLogFile('bar', 'instance')
        self.assertNotEqual(log_file, rds_file)

    def test_equals__w_size(self):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        rds_file = RdsLogFile('foo', 'instance')
        log_file.size = 1
        rds_file.size = 1
        self.assertEqual(log_file, rds_file)

    def test_not_equals__differ_size(self):
        log_file = S3LogFile('foo', 'bucket', 'prefix')
        rds_file = RdsLogFile('foo', 'instance')
        log_file.size = 1
        rds_file.size = 2
        self.assertTrue(log_file != rds_file)
        self.assertTrue(rds_file != log_file)
        self.assertFalse(log_file == rds_file)
        self.assertFalse(rds_file == log_file)


if __name__ == '__main__':
    unittest.main()
