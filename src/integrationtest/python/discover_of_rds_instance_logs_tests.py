from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3

from rds_log_dog.discoverer import Discoverer
from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.rds_instance import RDSInstance


class Test(unittest.TestCase):

    def test_log_file_handler_discover_rds_logfiles(self):
        disco = Discoverer()
        instances = disco.discover()
        self.assertLess(0, len(instances),
                        "We need at least one RDS instance for this test!")

        # pick one instance
        instance = instances.pop()

        client = boto3.client('rds')
        response = client.describe_db_log_files(DBInstanceIdentifier=instance.name)
        logfilehandler = LogFileHandler(RDSInstance(instance.name), 'b', 'p')
        discovered_logfiles = logfilehandler.discover_rds_logfiles()
        self.assertEqual(type(set()), type(discovered_logfiles))
        self.assertEqual(len(response['DescribeDBLogFiles']),
                    len(discovered_logfiles))

if __name__ == '__main__':
    unittest.main()
