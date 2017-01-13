from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import os, boto3
from util import execute_command
from cfn_utils import get_output

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open('target/FUNCTION_STACK_NAME','r') as f:
                self.function_stack_name = f.read().strip()

        self.lambda_function_name = get_output(self.function_stack_name, 'name')

    def invoke_lambda(self, name):
        client = boto3.client('lambda')
        response = client.invoke(FunctionName=name, LogType='Tail')
        return response

    def test_is_lambda_invokeable(self):
        response = self.invoke_lambda(self.lambda_function_name)
        self.assertNotIn('FunctionError', response, 'invocation error')

if __name__ == '__main__':
    unittest.main()

