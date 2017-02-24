from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import logging

import rds_log_dog.s3_utils
from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.log_file import RdsLogFile

from local import get_env
import utils

logger = logging.getLogger('ittest')


class TestLogFile(unittest.TestCase):

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

    @classmethod
    def tearDownClass(self):
        logger.info('cleanup: {}:{}'.format(self.bucket_name, self.dst_prefix))
        utils.delete_prefix(self.bucket_name, self.dst_prefix)

    def setUp(self):
        self.logfile_name = utils.choose_one_random_logfile_does_not_exists_in_s3(
            self.rds_instance.name, self.bucket_name)

    def test_logfile_rds_has_same_size_in_local(self):
        src = RdsLogFile(self.logfile_name, self.rds_instance.name)

    def test_logfile_equals_size(self):
        src = RdsLogFile(self.logfile_name, self.rds_instance.name)
        dst = self.lfh.copy(src)
        src.fetch_size()
        dst.fetch_size()
        self.assertEqual(src, dst)
        self.assertEqual(src.size, dst.size)

    def test_logfile_not_equals_size(self):
        src = RdsLogFile(self.logfile_name, self.rds_instance.name)
        dst = self.lfh.get_s3logfile(self.logfile_name)
        dst.write('')
        src.fetch_size()
        dst.fetch_size()
        self.assertNotEqual(src, dst)
        self.assertNotEqual(src.size, dst.size)

if __name__ == '__main__':
    from rds_log_dog.rds_log_dog import RDSLogDog
    RDSLogDog.setup_logger()
    unittest.main()
