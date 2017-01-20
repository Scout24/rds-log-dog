from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3

from utils import get_one_rds_instance
from local import execute_command, get_env

from rds_log_dog.discoverer import Discoverer
from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.log_file import LogFile
from rds_log_dog.rds_instance import RDSInstance


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.function_stack_name, self.bucket_stack_name,
         self.lambda_function_name, self.bucket_name) = get_env()

    def file_exists_in_s3(self, bucket, key):
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket)
        import pprint
        pprint.pprint(response)
        match = [o['Key'] for o in response['Contents'] if o['Key'] == key]
        return len(match) > 0

    def test_copy_rds_logfiles(self):
        instance = get_one_rds_instance()

        client = boto3.client('rds')
        response = client.describe_db_log_files(
            DBInstanceIdentifier=instance.name)
        src_logfile_name = response['DescribeDBLogFiles'][0]['LogFileName']
        logfile_to_copy = LogFile(src_logfile_name)
        expected_dst_key = 'ittest/{}'.format(instance.name, src_logfile_name)

        # check logfile doesn't exists in dst
        self.assertFalse(self.file_exists_in_s3(
            self.bucket_name, expected_dst_key))
        # discover logfiles and compare
        # TODO: extra test
        logfilehandler = LogFileHandler(RDSInstance(
            instance.name), self.bucket_name, 'ittest')
        logfiles = logfilehandler.discover_rds_logfiles()
        self.assertIn(logfile_to_copy, logfiles)

        # copy and check
        logfilehandler.copy(logfile_to_copy)
        self.assertTrue(self.file_exists_in_s3(
            self.bucket_name, expected_dst_key))


if __name__ == '__main__':
    unittest.main()
