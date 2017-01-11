import unittest

from rds_log_dog.main import Main

class TestMain(unittest.TestCase):

    def test_do_should_return_0(self):
        m = Main()
        self.assertEqual(0, m.do())

