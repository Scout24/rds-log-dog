from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
from moto import mock_s3

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

    @mock_s3
    def test_write(self):
        l = LogFile('foo')
        l.set_s3_dst('bucket', 'prefix')
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket='bucket')

        l.write('mydata')

        # must not throw an exception
        s3.head_object(Bucket='bucket', Key=l.get_s3_dst_key())


if __name__ == '__main__':
    unittest.main()
