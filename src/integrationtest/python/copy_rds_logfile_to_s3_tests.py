from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
import random
import logging

from utils import get_one_rds_instance
from local import execute_command, get_env

from rds_log_dog.discoverer import Discoverer
from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.log_file import LogFile, rdsLogFile
from rds_log_dog.rds_instance import RDSInstance
import utils

logger = logging.getLogger('iitest')


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.function_stack_name, self.bucket_stack_name,
         self.lambda_function_name, self.bucket_name) = get_env()
        self.dst_prefix = utils.get_temp_prefix()
        logger.info(
            'using s3 dst: {}/{}'.format(self.bucket_name, self.dst_prefix))
        self.rds_instance = utils.get_one_rds_instance()
        self.lfh = LogFileHandler(
            self.rds_instance, self.bucket_name, self.dst_prefix)

    def setUp(self):
        self.logfile_name = utils.choose_one_random_logfile_does_not_exists_in_s3(
            self.rds_instance.name, self.bucket_name)

    @classmethod
    def tearDownClass(self):
        logger.info('cleanup: {}:{}'.format(self.bucket_name, self.dst_prefix))
        utils.delete_prefix(self.bucket_name, self.dst_prefix)

    def test_copy_rds_logfiles(self):
        logfile_to_copy = rdsLogFile(self.logfile_name, self.rds_instance.name)

        # discover logfiles and compare
        # TODO: extra test
        logfiles = self.lfh.discover_logfiles_in_rds()
        self.assertIn(logfile_to_copy, logfiles)

        # copy and check
        self.lfh.copy(logfile_to_copy)
        expected_dst_key = "{}/{}/{}".format(self.dst_prefix,
                                             self.rds_instance.name,
                                             self.logfile_name)
        self.assertTrue(utils.file_exists_in_s3(
            self.bucket_name, expected_dst_key), "logfile not found in s3 {}".format(expected_dst_key))


if __name__ == '__main__':
    unittest.main()
