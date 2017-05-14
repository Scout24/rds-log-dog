from __future__ import print_function, absolute_import, division

import os
import logging
from tempfile import NamedTemporaryFile

import boto3
import unittest2 as unittest
from moto import mock_s3

from rds_log_dog.s3_utils import (
    debug_dir_of_file,
    list_folders, get_top_level_folder_under_prefix,
    write_data_to_object, get_size, get_files, copy)


class TestS3Utils(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.s3 = boto3.client('s3')

    @mock_s3
    def test_get_files(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='foo/file')
        self.s3.put_object(Bucket='mybucket', Key='foo/file1')
        self.assertEqual([('foo/file', 0), ('foo/file1', 0)],
                         get_files('mybucket', 'foo'))

    @mock_s3
    def test_get_files_with_more_than_max_keys(self):
        '''
        Test if get_files fetches all files, regardless of
        how many files. Default behaviour only fetches 1000
        w/o paginating the response.
        This test depends on moto>=0.4.32
        '''
        expected_list_of_files = []
        bucket_name = 'mybucket'
        self.s3.create_bucket(Bucket=bucket_name)
        for i in range(0, 5):
            key = 'foo/file{}'.format(i)
            self.s3.put_object(Bucket=bucket_name, Key=key)
            expected_list_of_files.append(('{}'.format(key), 0))
        files = get_files(bucket_name, 'foo', 2)
        self.assertEqual(expected_list_of_files, files)

    @mock_s3
    def test_list_s3_folders_on_non_existing_folder(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.assertEqual(set(), list_folders(
            bucket='mybucket', prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_on_empty_folder(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='folder1/')
        self.assertEqual(set(), list_folders(
            bucket='mybucket', prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_on_only_files(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='folder1/file1')
        self.assertEqual(set(), list_folders(
            bucket='mybucket', prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_flat(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file2')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder2/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/file1')
        self.assertEqual({'folder1', 'folder2'}, list_folders(
            bucket='mybucket', prefix='rds_logs'))

    @mock_s3
    def test_list_s3_folders_nested(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket',
                           Key='rds_logs/folder1/subfolder1/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file2')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder2/file1')
        self.assertEqual({'folder1', 'folder2'}, list_folders(
            bucket='mybucket', prefix='rds_logs'))

    def test_get_top_level_folder_under_prefix_top_level_folder(self):
        self.assertEqual('folder1', get_top_level_folder_under_prefix(
            'rds_log/folder1/', 'rds_log'))

    def test_get_top_level_folder_under_prefix_2nd_level_folder(self):
        self.assertEqual('folder1', get_top_level_folder_under_prefix(
            'rds_log/folder1/subfolder/', 'rds_log'))

    def test_get_top_level_folder_under_prefix_2nd_level_file(self):
        self.assertEqual('folder1', get_top_level_folder_under_prefix(
            'rds_log/folder1/file', 'rds_log'))

    def test_get_top_level_folder_under_prefix_top_level_file(self):
        self.assertEqual(None, get_top_level_folder_under_prefix(
            'rds_log/folder1', 'rds_log'))

    def test_get_top_level_folder_under_prefix_with_tricky_foldername(self):
        self.assertEqual('id', get_top_level_folder_under_prefix(
            'rds_log/id/', 'rds_log'))
        self.assertEqual('rds_id', get_top_level_folder_under_prefix(
            'rds_log/rds_id/', 'rds_log'))

    # TODO/FIXME: unimplemented or wrong usage
    def test_get_top_level_folder_under_prefix_with_parent_end_w_slash(self):
        # wrong
        self.assertEqual('older1', get_top_level_folder_under_prefix(
            'rds/folder1/', 'rds/'))
        # right
        self.assertEqual(None, get_top_level_folder_under_prefix(
            'rds/folder1', 'rds/'))

    # TODO/FIXME: unimplemented or wrong usage
    def test_get_top_level_folder_under_prefix_with_no_parent(self):
        with self.assertRaises(Exception):
            self.assertEqual(None, get_top_level_folder_under_prefix(
                'rds/folder1/', None))

    @mock_s3
    def test_write_data_to_object(self):
        self.s3.create_bucket(Bucket='bucket')

        write_data_to_object('bucket', 'foo', 'mydata')

        # must not throw an exception
        self.s3.head_object(Bucket='bucket', Key='foo')

    @mock_s3
    def test_copy(self):
        self.s3.create_bucket(Bucket='bucket')
        with NamedTemporaryFile() as tempfile:
            tempfile.write('foo')
            file_size = os.path.getsize(tempfile.name)
            copy('bucket', 'foo', tempfile.name)
        self.assertEqual(file_size, get_size('bucket', 'foo'))

    @mock_s3
    def test_get_size(self):
        with NamedTemporaryFile() as tempfile:
            tempfile.write('Some Datafoo')
            file_size = os.path.getsize(tempfile.name)
            self.s3.create_bucket(Bucket='foo')
            self.s3.put_object(
                Body=tempfile,
                Bucket='foo',
                Key='bar'
            )
            self.assertEquals(file_size, get_size('foo', 'bar'))

    def test__debug_file_sizes(self):
        logging.getLogger().setLevel('DEBUG')
        with NamedTemporaryFile() as temp_file:
            temp_file.write('')
            debug_dir_of_file(temp_file)
        self.fail()


if __name__ == '__main__':
    unittest.main()
