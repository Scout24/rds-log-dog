from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import logging

from local import get_env
import utils
from rds_log_dog.rds_log_dog import RDSLogDog
from rds_log_dog.log_file import S3LogFile
from rds_log_dog.config import Config
from rds_log_dog.log_file_handler import LogFileHandler
import rds_log_dog.s3_utils as s3
import rds_log_dog.rds_utils as rds

logger = logging.getLogger(__name__)


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.function_stack_name, self.bucket_stack_name,
         self.lambda_function_name, self.bucket_name) = get_env()
        self.dst_prefix = utils.get_temp_prefix()
        logger.info(
            'using tmp s3 dst: {}/{}'.format(self.bucket_name, self.dst_prefix))
        self.rds_instance = utils.get_one_rds_instance()
        self.lfh = LogFileHandler(
            self.rds_instance, self.bucket_name, self.dst_prefix)
        self.config = Config(self.bucket_name, prefix=self.dst_prefix)

    def setUp(self):
        self.logfile_name = utils.get_one_random_logfile(
            self.rds_instance.name)

    @classmethod
    def tearDownClass(self):
        logger.info('cleanup: {}:{}'.format(self.bucket_name, self.dst_prefix))
        #utils.delete_prefix(self.bucket_name, self.dst_prefix)

    def test_sync_one__instance(self):
        logger.info('[test] sync one instance ...')
        rds_log_dog = RDSLogDog(self.config)
        rds_log_dog.process_instance(self.rds_instance)
        files_s3 = s3.get_files(self.bucket_name, self.dst_prefix)
        files_rds = rds.describe_logfiles_of_instance(self.rds_instance.name)
        self.assertEqual(len(files_s3)-1, len(files_rds))
        
    def test_sync_one_file_with_differs_in_size(self):
        logger.info('[test] redownloading file ...')
        rds_log_dog = RDSLogDog(self.config)
        rds_log_dog.process_instance(self.rds_instance)

        # choose a random file to reduce filesize in s3 to trigger redownload
        logfile = utils.get_one_random_logfile(self.rds_instance.name)
        lf = S3LogFile(logfile, self.bucket_name, "{}/{}".format(self.dst_prefix, self.rds_instance.name))
        logger.debug('truncate size of {}'.format(lf.name))
        lf.fetch_size()
        size = lf.size
        s3.write_data_to_object(lf.bucket, lf.get_dst_key(), 'foooooo')
        lf.fetch_size()
        logger.debug('new size of {} is {}'.format(lf.name, lf.size))
        self.assertNotEqual(size, lf.size)
        logger.debug('reprocessing instance ...')
        rds_log_dog.process_instance(self.rds_instance)
        lf.fetch_size()
        self.assertEqual(size, lf.size) 


if __name__ == '__main__':
    RDSLogDog.setup_logger()
    unittest.main()
