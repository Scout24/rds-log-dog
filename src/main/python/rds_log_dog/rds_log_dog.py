from __future__ import print_function, absolute_import, unicode_literals, division

import logging
from .discoverer import Discoverer
from .log_file_handler import LogFileHandler

logger = logging.getLogger(__name__)


class RDSLogDog(object):  # pragma: no cover

    def __init__(self, config):
        self.setup_logger()
        self.s3_dst_bucket = config.s3_dst_bucket
        self.s3_dst_prefix_for_logs = config.s3_prefix_for_logs

    def setup_logger(name):
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        # disable botocore logging in debug level
        logger = logging.getLogger('botocore')
        logger.setLevel(logging.WARN)

    def do(self):
        # setup things

        # discover()
        discoverer = Discoverer()
        instances = discoverer.discover()
        logger.info("{} instances discovered.".format(len(instances)))
        for instance in instances:
            logger.info("processing: '{}'".format(instance.name))
            logfilehandler = LogFileHandler(
                instance,
                self.s3_dst_bucket,
                self.s3_dst_prefix_for_logs)
            logfilehandler.setup_s3_destination()
            files_in_s3 = logfilehandler.discover_s3_logfiles()
            logger.info("found {} files in s3".format(len(files_in_s3)))
            files_in_rds = logfilehandler.discover_rds_logfiles()
            logger.info("found {} files in rds".format(len(files_in_rds)))
            logfiles_to_copy = logfilehandler.new_logfiles(
                files_in_rds, files_in_s3)
            logger.info("going to copy {} logfiles ...".format(
                len(logfiles_to_copy)))
            for file in logfiles_to_copy:
                logger.debug("copying {} ...".format(file))
                logfilehandler.copy(file)
            # write metric / logentry

        return 0
