from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3 as boto
from moto import mock_s3
from rds_log_dog.s3_utils import list_folders

class TestS3Utils(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.s3 = boto.client('s3')

    @mock_s3
    def test_list_s3_folders_on_empty(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='folder1/')
        self.assertEqual([], list_folders(Bucket='mybucket', Prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_on_only_files(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='folder1/file1')
        self.assertEqual([], list_folders(Bucket='mybucket', Prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_flat(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file2')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder2/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/file1')
        self.assertEqual(['folder1', 'folder2'], list_folders(Bucket='mybucket', Prefix='rds_logs'))

    @mock_s3
    def test_list_s3_folders_nested(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/subfolder1/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file2')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder2/file1')
        self.assertEqual(['folder1', 'folder2'], list_folders(Bucket='mybucket', Prefix='rds_logs'))

if __name__ == '__main__':
    unittest.main()  
