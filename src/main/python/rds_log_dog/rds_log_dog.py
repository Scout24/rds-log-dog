from __future__ import print_function, absolute_import, unicode_literals, division

class RDSLogDog(object):

    def do(self):
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

