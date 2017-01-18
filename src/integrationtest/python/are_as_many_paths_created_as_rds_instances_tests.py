from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import os
import re
from local import execute_command, get_env
import rds_log_dog.s3_utils


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.function_stack_name, self.bucket_stack_name,
         self.lambda_function_name, self.bucket_name) = get_env()

    def test_no_s3_rds_logs_equals_rds_instances(self):
        folder_result = rds_log_dog.s3_utils.list_folders(
            self.bucket_name, 'rds_logs')

        # discover # of rds instances
        import boto3
        client = boto3.client('rds')
        response = client.describe_db_instances()

        self.assertEqual(len(response['DBInstances']), len(
            folder_result), "number of rds instances doesn't match number of folders in rds_logs/")

if __name__ == '__main__':
    unittest.main()
