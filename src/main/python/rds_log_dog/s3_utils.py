from __future__ import print_function, absolute_import, unicode_literals, division

import boto3 

def list_folders(Bucket, Prefix):
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=Bucket, Prefix=Prefix)
    if response['IsTruncated']:
        raise Exception("bucket have more than 1000 keys - not implemented until now")
    folders = set()
    for key_struct in response['Contents']:
        key_without_pref = key_struct['Key'].lstrip(Prefix + '/')
        if key_without_pref.find('/') > 0:
            key_first_level = key_without_pref.split('/')[0]
            folders.add(key_first_level)
    return(folders)
