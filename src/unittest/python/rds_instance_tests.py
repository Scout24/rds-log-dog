import unittest2 as unittest
from rds_log_dog.rds_instance import RDSInstance


class Test(unittest.TestCase):

    def test_get_id(self):
        rds = RDSInstance('foo')
        self.assertEqual('foo', rds.get_id())
