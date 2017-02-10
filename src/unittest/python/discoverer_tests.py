from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
from moto import mock_rds
from rds_log_dog.discoverer import Discoverer

import os

# Else we run into problems with mocking
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = ''
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'


class Test(unittest.TestCase):

    @mock_rds
    def fest_discoverer_discover_with_no_rds_instances(self):
        disco = Discoverer()
        disco_result = disco.discover()
        self.assertEqual([], disco_result, "count rds-instances should be 0 in moto-mock env and from type list")

if __name__ == '__main__':
    unittest.main()

