from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
from mock import patch, Mock

from rds_log_dog.log_file import LogFile


class Test(unittest.TestCase):

    def test_set_s3_dst(self):
        l = LogFile('foo')
        l.set_s3_dst('bucket', 'prefix')
        self.assertEqual('bucket', l.bucket)
        self.assertEqual('prefix', l.prefix)

    def test_get_s3_dst_key(self):
        l = LogFile('foofile')
        l.set_s3_dst('bucket', 'prefix')
        self.assertEqual('prefix/foofile', l.get_s3_dst_key())

    @patch('rds_log_dog.rds_utils.get_full_db_logfile_data')
    def test_read_from_rds(self, get_full_db_logfile_data):
        l = LogFile('foofile')
        l.set_rds_src('foords')
        l.ensure_logfile_is_rds_logfile = Mock()
        l.read_data()
        l.ensure_logfile_is_rds_logfile.assert_called()
        self.assertTrue(get_full_db_logfile_data.called)

    @patch('rds_log_dog.s3_utils.write_data_to_object')
    def test_write_logfile_data(self, write_data_to_object):
        l = LogFile('foofile')
        l.set_s3_dst('foo', 'bar')
        l.ensure_logfile_is_s3_logfile = Mock()
        l.write_data('data')
        l.ensure_logfile_is_s3_logfile.assert_called()
        self.assertTrue(write_data_to_object.called)

    @patch('rds_log_dog.rds_utils.get_size')
    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size(self, s3_get_size, rds_get_size):
        l = LogFile('foo')
        l.set_s3_dst('foo', 'bar')
        l.set_rds_src('foo')
        s3_get_size.return_value = 23
        rds_get_size.return_value = 42
        l.fetch_size()
        self.assertEqual(23, l.s3_size)
        self.assertEqual(42, l.rds_size)

    @patch('rds_log_dog.rds_utils.get_size')
    @patch('rds_log_dog.s3_utils.get_size')
    def test_fetch_size__calls(self, s3_get_size, rds_get_size):
        l = LogFile('foo')
        l.fetch_size()
        self.assertFalse(s3_get_size.called)
        self.assertFalse(rds_get_size.called)

        l.set_s3_dst('foo', 'bar')
        l.fetch_size()
        self.assertTrue(s3_get_size.called)
        self.assertFalse(rds_get_size.called)

        l.set_rds_src('foo')
        l.fetch_size()
        self.assertTrue(s3_get_size.called)
        self.assertTrue(rds_get_size.called)

    def wip_test_copy(self):
       l = LogFile('foofile')
       l.set_rds_src('foo')
       l.set_s3_dst('bucket', 'prefix')
       l.copy()

    def test_logfile_is_rds_logfile(self):
        l = LogFile('foo')
        self.assertFalse(l.logfile_is_rds_logfile())
        l.set_rds_src('foo')
        self.assertTrue(l.logfile_is_rds_logfile())

    def test_logfile_is_s3_logfile(self):
        l = LogFile('foo')
        self.assertFalse(l.logfile_is_s3_logfile())
        l.set_s3_dst('foo', 'bar')
        self.assertTrue(l.logfile_is_s3_logfile())
       

if __name__ == '__main__':
    unittest.main()
