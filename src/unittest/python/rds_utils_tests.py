from __future__ import print_function, absolute_import, division

import unittest2 as unittest
from mock import patch

from rds_log_dog.rds_utils import get_size


class Test(unittest.TestCase):

    @patch('rds_log_dog.rds_utils.describe_logfiles_of_instance')
    def test_get_size(self, describe_logfiles_of_instance):
        describe_logfiles_of_instance.return_value = [
            dict(LogFileName='foo', LastWritten='bar', Size=42),
            dict(LogFileName='foo2', LastWritten='bar', Size=23)]
        self.assertEqual(42, get_size('foo', 'foo'))
