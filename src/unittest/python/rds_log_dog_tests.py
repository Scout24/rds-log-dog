import unittest

from rds_log_dog.rds_log_dog import RDSLogDog


class TestRDSLogDog(unittest.TestCase):

    def test_do_should_return_0(self):
        m = RDSLogDog()
        self.assertEqual(0, m.do())
