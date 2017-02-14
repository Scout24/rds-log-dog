from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
from mock import patch, Mock

from rds_log_dog.log_file import LogFile, S3LogFile, RdsLogFile


class Test(unittest.TestCase):

    def test_S3LogFile_init(self):
        l = S3LogFile('foo', 'bucket', 'prefix')
        self.assertEqual('foo', l.name)
        self.assertEqual('prefix', l.prefix)
        self.assertEqual('bucket', l.bucket)

    def test_RdsLogFile_init(self):
        l = RdsLogFile('foo', 'instance')
        self.assertEqual('foo', l.name)
        self.assertEqual('instance', l.instance_name)

    @patch('rds_log_dog.rds_utils.get_full_db_logfile_data')
    def test_read_from_rds(self, get_full_db_logfile_data):
        l = RdsLogFile('foofile', 'instance')
        get_full_db_logfile_data.return_value = 'data'
        result = l.read()
        get_full_db_logfile_data.assert_called_with('instance', 'foofile')
        self.assertEqual('data', result)

    @patch('rds_log_dog.s3_utils.write_data_to_object')
    def test_write_to_s3(self, write_data_to_object):
        l = S3LogFile('name', 'bucket', 'prefix')
        l.write('data')
        write_data_to_object.assert_called_with(
            'bucket', 'prefix/name', 'data')

    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size_s3(self, get_size):
        l = S3LogFile('foo', 'bucket', 'prefix')
        get_size.return_value = 23
        l.fetch_size()
        get_size.assert_called_with('bucket', l.get_dst_key())
        self.assertEqual(23, l.size)

    @patch('rds_log_dog.rds_utils.get_size')
    def test_fetch_size_rds(self, get_size):
        l = RdsLogFile('foo', 'instance')
        get_size.return_value = 23
        l.fetch_size()
        get_size.assert_called_with('instance', 'foo')
        self.assertEqual(23, l.size)

    @patch('rds_log_dog.rds_utils.get_size')
    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size_s3__calls(self, s3_get_size, rds_get_size):
        s3 = S3LogFile('foo', 'bucket', 'prefix')
        s3.fetch_size()
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
        s3 = S3LogFile('name', 'bucket', 'prefix')
        self.assertEqual('prefix/name', s3.get_dst_key())

    def test_equals__wo_size(self):
        l1 = S3LogFile('foo', 'bucket', 'prefix')
        l2 = RdsLogFile('foo', 'instance')
        self.assertEqual(l1, l2)

    def test_not_equals__wo_size(self):
        l1 = S3LogFile('foo', 'bucket', 'prefix')
        l2 = RdsLogFile('bar', 'instance')
        self.assertNotEqual(l1, l2)

    def test_equals__w_size(self):
        l1 = S3LogFile('foo', 'bucket', 'prefix')
        l2 = RdsLogFile('foo', 'instance')
        l1.size = 1
        l2.size = 1
        self.assertEqual(l1, l2)

    def test_not_equals__differ_size(self):
        l1 = S3LogFile('foo', 'bucket', 'prefix')
        l2 = RdsLogFile('foo', 'instance')
        l1.size = 1
        l2.size = 2
        self.assertNotEqual(l1, l2)


if __name__ == '__main__':
    unittest.main()
