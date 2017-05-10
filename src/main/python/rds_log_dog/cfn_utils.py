from __future__ import print_function, absolute_import, division

import boto3


def cfn_get_output(stack_name, key):
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    return [o['OutputValue'] for o in outputs if o['OutputKey'] == key][0]
