from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import os, re
from util import execute_command
from cfn_utils import get_output

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open('target/DST_BUCKET_STACK_NAME','r') as f:
                self.bucket_stack_name = f.read().strip()

        self.bucket_name = get_output(self.bucket_stack_name , 'name')

    def test_s3_rds_logs_dst_exists(self):
        return_code, std_out, std_err = execute_command('aws s3 ls {}'.format(self.bucket_name))
        out = std_out.splitlines()
        result = [ line for line in out if re.match("^\s*PRE\s*{}\s*".format('rds_logs'), line) ]
        self.assertEqual(1, len(result), "rds_log/ not found")

if __name__ == '__main__':
    unittest.main()
