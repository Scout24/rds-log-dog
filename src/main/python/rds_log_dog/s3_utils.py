from __future__ import print_function, absolute_import, unicode_literals, division

import boto3
import logging

logger = logging.getLogger(__name__)

def get_top_level_folder_under_prefix(prefix, parent_prefix):
    chars_to_strip = len(parent_prefix) + 1
    stripped_prefix = prefix[chars_to_strip:]
    if '/' in stripped_prefix:
        return stripped_prefix.split('/')[0]
    return None


def list_folders(Bucket, Prefix):
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=Bucket, Prefix=Prefix)
    if response['IsTruncated']:
        raise Exception(
            "bucket have more than 1000 keys - not implemented until now")
    folders = set()
    if 'Contents' in response:
        for key_struct in response['Contents']:
            folder = get_top_level_folder_under_prefix(
                key_struct['Key'], Prefix)
            if folder:
                folders.add(folder)
    else:
        logger.warn(
            'list on prefix: {}/{} not possible. Does it exists ?'.format(Bucket, Prefix))
    return folders


def get_files(bucket, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(
        Bucket=bucket, Prefix=prefix)
    if 'Contents' in response:
        return [o['Key'] for o in response['Contents']]
    return None


def write_data_to_object(bucket, object_key, data):
    client = boto3.client('s3')
    client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=data)


def setup_s3_destination(dst_bucket, dst_prefix_instance):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(
        Bucket=dst_bucket, Prefix=dst_prefix_instance)
    if 'Contents' not in response:
        s3.put_object(
            Bucket=dst_bucket, Key='{}/'.format(dst_prefix_instance))
        logger.debug('created missing s3 dest: {}'.format(
            dst_prefix_instance))