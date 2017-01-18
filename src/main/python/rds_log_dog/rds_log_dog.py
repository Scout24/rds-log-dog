from __future__ import print_function, absolute_import, unicode_literals, division

from .config import get_logger
from .discoverer import Discoverer
from .log_file_handler import LogFileHandler

logger = get_logger(__name__)


class RDSLogDog(object):

    def __init__(self, config):
        self.s3_dst_bucket = config.s3_dst_bucket
        self.s3_dst_prefix_for_logs = config.s3_prefix_for_logs

    def do(self):
        # setup things

        # discover()
        discoverer = Discoverer()
        instances = discoverer.discover()
        logger.info("{} instances discovered.".format(len(instances)))
        for instance in instances:
            logger.info("processing: {}".format(instance.name))
            logfilehandler = LogFileHandler(
                instance,
                self.s3_dst_bucket,
                self.s3_dst_prefix_for_logs)
            logfilehandler.setup_s3_destination()
            # discover_s3_logfiles()
            # discover_rds_logfiles()
            # foreach logfile in new_logfiles()
            # copy_logfile()
            # write metric / logentry

        return 0
