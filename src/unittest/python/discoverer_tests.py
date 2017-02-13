from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
from moto import mock_rds
from rds_log_dog.discoverer import Discoverer

try:
    import _fix_moto as fix
    fix.unset_http_proxy()
except:
    pass


class Test(unittest.TestCase):

    @mock_rds
    def test_discoverer_discover_with_no_rds_instances(self):
        disco = Discoverer()
        disco_result = disco.discover()
        self.assertEqual([], disco_result, "count rds-instances should be 0 in moto-mock env and from type list")

if __name__ == '__main__':
    unittest.main()

