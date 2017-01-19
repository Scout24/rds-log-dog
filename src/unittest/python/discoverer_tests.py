from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
from moto import mock_rds
from rds_log_dog.discoverer import Discoverer


class Test(unittest.TestCase):

    @mock_rds
    def test_discoverer_discover(self):
        disco = Discoverer()
        disco_result = disco.discover()
        self.assertEqual(len(disco_result), 0, "count rds-instances should be 0 in moto-mock env")

if __name__ == '__main__':
    unittest.main()

