from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
from rds_log_dog.discoverer import Discoverer
from rds_log_dog.log_file_handler import rds_logfiles


class Test(unittest.TestCase):

    def test_log_file_handler_discover_rds_logfiles(self):
        disco = Discoverer()
        instances = disco.discover()
        self.assertGreater(0, len(instances),
                           "We need at least one RDS instance for this test!")

        # pick one instance
        instance = instances.pop()

        client = boto3.client('rds')
        response = client.describe_db_logfiles(instance.name)
        discovered_logfile = discover_rds_logfiles(instance.name)
        assertEqual('set', type(discovered_logfile))
        assertEqual(len(response['DescribeDBLogFiles']),
                    len(discovered_logfiles))

if __name__ == '__main__':
    unittest.main()
