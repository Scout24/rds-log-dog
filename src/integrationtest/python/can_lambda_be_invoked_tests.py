from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import base64

from local import execute_command
from utils import invoke_lambda


class Test(unittest.TestCase):

    def test_is_lambda_invokeable(self):
        response = invoke_lambda()
        self.assertNotIn('FunctionError', response, 'invocation error.\n response: {}'.format(base64.b64decode(response['LogResult'])))

if __name__ == '__main__':
    #unittest.main()
    pass
