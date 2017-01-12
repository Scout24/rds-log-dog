from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import os, re
from util import execute_command

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open('target/FUNCTION_STACK_NAME','r') as f:
                self.function_stack_name = f.read().strip()

        with open('target/DST_BUCKET_STACK_NAME','r') as f:
                self.bucket_stack_name = f.read().strip()

        self.lambda_function_name = self.get_output(self.function_stack_name, 'name')
        self.bucket_name = self.get_output(self.bucket_stack_name , 'name')
        
    @classmethod
    def get_output(self, stack_name, key):
        import boto3
        client = boto3.client('cloudformation')
        response = client.describe_stacks(StackName=self.bucket_stack_name)
        outputs = response['Stacks'][0]['Outputs']
        return [o['OutputValue'] for o in outputs if o['OutputKey'] == key][0]

    def test_s3_rds_logs_dst_exists(self):
        print("checking if ",self.bucket_name, " exists")
        return_code, std_out, std_err = execute_command('aws s3 ls {}'.format(self.bucket_name))
        out = std_out.splitlines()
        result = [ line for line in out if re.match("^\s*PRE\s*{}\s*".format('rds_logs'), line) ]
        self.assertEqual(1, len(result), "rds_log/ not found")

    def test_no_s3_rds_logs_equals_rds_instances(self):
        return_code, std_out, std_err = execute_command('aws s3 ls {}/rds_logs/'.format(self.bucket_name))
        out = std_out.splitlines()
        result = [ line for line in out if re.match("^\s*PRE\s+", line) ]
        self.assertEqual(-1, len(result), "TODO: compare no. prefixes with no. instances")

if __name__ == '__main__':
    unittest.main()
