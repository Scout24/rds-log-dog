from __future__ import print_function, absolute_import, unicode_literals, division

import boto3
from .config import get_logger


def get_top_level_folder_under_prefix(prefix, parent_prefix):
    chars_to_strip = len(parent_prefix) + 1
    stripped_prefix = prefix[chars_to_strip:]
    if '/' in stripped_prefix:
        return stripped_prefix.split('/')[0]
    return None


def list_folders(Bucket, Prefix):
    logger = get_logger(__name__)
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
