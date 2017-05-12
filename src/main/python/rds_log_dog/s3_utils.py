from __future__ import print_function, absolute_import, division

import logging
import boto3

logger = logging.getLogger(__name__)


def get_top_level_folder_under_prefix(prefix, parent_prefix):
    chars_to_strip = len(parent_prefix) + 1
    stripped_prefix = prefix[chars_to_strip:]
    if '/' in stripped_prefix:
        return stripped_prefix.split('/')[0]
    return None


def list_folders(bucket, prefix):
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if response['IsTruncated']:
        raise Exception(
            "bucket have more than 1000 keys - not implemented until now")
    folders = set()
    if 'Contents' in response:
        for key_struct in response['Contents']:
            folder = get_top_level_folder_under_prefix(
                key_struct['Key'], prefix)
            if folder:
                folders.add(folder)
    else:
        logger.warn(
            'list on prefix: %s/%s not possible. Does it exists ?',
            bucket, prefix)
    return folders


def _get_key_and_size(list_objects_response):
    keys = []
    if 'Contents' in list_objects_response:
        keys.extend(
            [(o['Key'], o['Size']) for o in list_objects_response['Contents']])
    else:
        '''
        no clue, how to deal with this and when this happens.
        So print a warning.
        '''
        logger.warn('response content is empty. Check results if in doubt.')
    return keys


def get_files(bucket, prefix, max_files_in_response=1000):
    '''
    Get _all_ keys of a given bucket and prefix in s3

    param max_files_in_response is for testing full fetch of all keys/files
    if we have more keys than 1000 (which is the maximum of the api)
    see: http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects_v2
    '''
    list_of_files = []
    client = boto3.client('s3')
    next_continuation_token = ''
    while True:
        response = client.list_objects_v2(
            Bucket=bucket, Prefix=prefix,
            MaxKeys=max_files_in_response,
            ContinuationToken=next_continuation_token)
        list_of_files.extend(_get_key_and_size(response))
        if response['IsTruncated']:
            next_continuation_token = response['NextContinuationToken']
        else:
            break
    return list_of_files


def write_data_to_object(bucket, object_key, data):
    client = boto3.client('s3')
    client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=data)


def copy(bucket, object_key, filename):
    logger.debug('copying %r to s3://%s/%s', filename, bucket, object_key)
    client = boto3.client('s3')
    client.upload_file(filename, bucket, object_key)


def setup_s3_destination(dst_bucket, dst_prefix_instance):
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=dst_bucket, Prefix=dst_prefix_instance)
    if 'Contents' not in response:
        client.put_object(
            Bucket=dst_bucket, Key='{}/'.format(dst_prefix_instance))
        logger.debug('created missing s3 dest: %s', dst_prefix_instance)


def get_size(bucket, key):
    client = boto3.client('s3')
    response = client.head_object(Bucket=bucket, Key=key)
    return response['ContentLength']
