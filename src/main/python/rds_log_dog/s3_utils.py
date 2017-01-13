from __future__ import print_function, absolute_import, unicode_literals, division

import boto3 as boto

def list_folders(Bucket, Prefix):
    REGION = 'eu-west-1'
    client_handler = boto.client('s3', region_name=REGION)
    response_handler = client_handler.list_objects_v2(Bucket=Bucket, Prefix=Prefix)
    if response_handler['ResponseMetadata']['HTTPStatusCode'] == 200:
        set_dirs = set()
        for key_struct in response_handler[u'Contents']:
            key_without_pref = key_struct[u'Key'].lstrip(Prefix + '/')
            key_first_level = key_without_pref.split('/')[0]
            set_dirs.add(key_first_level)
        return(set_dirs)
    else:
        raise Exception("list_objects_v2 returned with HTTPStatusCode <> 200")
