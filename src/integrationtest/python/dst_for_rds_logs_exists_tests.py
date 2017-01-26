from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest

from local import execute_command

import rds_log_dog.s3_utils
from rds_log_dog.cfn_utils import cfn_get_output
from rds_log_dog.discoverer import Discoverer

from utils import invoke_lambda


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open('target/DST_BUCKET_STACK_NAME', 'r') as f:
            self.bucket_stack_name = f.read().strip()

        self.bucket_name = cfn_get_output(self.bucket_stack_name, 'name')
        invoke_lambda()

    def test_s4_rds_logs_dst_exists(self):
        folder_result = rds_log_dog.s3_utils.list_folders(
            self.bucket_name, 'rds_logs')
        disco = Discoverer()
        disco_result = disco.discover()
        self.assertEqual(len(disco_result), len(folder_result),
                         "count rds-instances do not match rds_log-folders")

if __name__ == '__main__':
    unittest.main()
