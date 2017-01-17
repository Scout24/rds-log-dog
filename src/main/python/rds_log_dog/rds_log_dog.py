from __future__ import print_function, absolute_import, unicode_literals, division

from .config import get_logger


class RDSLogDog(object):

    def do(self):
        logger = get_logger(__name__)
        logger.info('start')
        # setup things

        # s3 dest path
        # discover()
        # foreach instance do
        # discover_rds_logfiles()
        # discover_s3_logfiles()
        # foreach logfile in new_logfiles()
        # copy_logfile()
        # write metric / logentry
        return 0
