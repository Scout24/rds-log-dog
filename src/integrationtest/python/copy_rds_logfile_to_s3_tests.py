from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
import random

from utils import get_one_rds_instance
from local import execute_command, get_env

from rds_log_dog.discoverer import Discoverer
from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.log_file import LogFile
from rds_log_dog.rds_instance import RDSInstance
import rds_log_dog.rds_utils as rds


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.function_stack_name, self.bucket_stack_name,
         self.lambda_function_name, self.bucket_name) = get_env()

    def file_exists_in_s3(self, bucket, key):
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket)
        match = [o['Key'] for o in response['Contents'] if o['Key'] == key]
        return len(match) > 0

    def get_one_random_logfile(self, instance_name):
        logfiles = rds.describe_logfiles_of_instance(instance_name)
        return logfiles[random.choice(range(0, len(logfiles) - 1))]['LogFileName']

    def test_copy_rds_logfiles(self):
        instance = get_one_rds_instance()
        src_logfile_name = self.get_one_random_logfile(
            instance.name)
        logfile_to_copy = LogFile(src_logfile_name)
        expected_dst_key = 'ittest/{}/{}'.format(
            instance.name, src_logfile_name)

        # check logfile doesn't exists in dst
        self.assertFalse(self.file_exists_in_s3(
            self.bucket_name, expected_dst_key), "destination logfile already exists in s3 {}/{}. Can't test to copy.".format(self.bucket_name, expected_dst_key))
        # discover logfiles and compare
        # TODO: extra test
        logfilehandler = LogFileHandler(RDSInstance(
            instance.name), self.bucket_name, 'ittest')
        logfiles = logfilehandler.discover_logfiles_in_rds()
        self.assertIn(logfile_to_copy, logfiles)

        # copy and check
        logfilehandler.copy(logfile_to_copy)
        self.assertTrue(self.file_exists_in_s3(
            self.bucket_name, expected_dst_key), "logfile not found in s3 {}".format(expected_dst_key))


if __name__ == '__main__':
    unittest.main()
