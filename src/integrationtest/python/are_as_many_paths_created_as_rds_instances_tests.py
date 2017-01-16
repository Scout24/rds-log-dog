from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import os, re
from util import execute_command
from cfn_utils import get_output
import rds_log_dog.s3_utils

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open('target/FUNCTION_STACK_NAME','r') as f:
                self.function_stack_name = f.read().strip()

        with open('target/DST_BUCKET_STACK_NAME','r') as f:
                self.bucket_stack_name = f.read().strip()

        self.lambda_function_name = get_output(self.function_stack_name, 'name')
        self.bucket_name = get_output(self.bucket_stack_name , 'name')
       
    def test_no_s3_rds_logs_equals_rds_instances(self):
        folder_result = rds_log_dog.s3_utils.list_folders(self.bucket_name,'rds_logs')

        # discover # of rds instances
        import boto3
        client = boto3.client('rds')
        response = client.describe_db_instances()

        self.assertEqual(len(response['DBInstances']), len(folder_result), "number of rds instances doesn't match number of folders in rds_logs/")

if __name__ == '__main__':
    unittest.main()
