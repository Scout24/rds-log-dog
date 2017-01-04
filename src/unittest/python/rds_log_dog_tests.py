import unittest

from rds_log_dog import hello

class TestHello(unittest.TestCase):

    def test_should_return_hello(self):
        self.assertEqual('hello world', hello())
