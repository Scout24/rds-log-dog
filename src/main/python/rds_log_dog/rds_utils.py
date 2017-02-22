from __future__ import print_function, absolute_import, unicode_literals, division

import logging
import json
import boto3

logger = logging.getLogger(__name__)


def describe_logfiles_of_instance(name):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    response = client.describe_db_log_files(
        DBInstanceIdentifier=name)
    if 'DescribeDBLogFiles' in response:
        return response['DescribeDBLogFiles']
    return []


def download(instance_name, logfile_name, fh):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    next_position_marker = '0'
    logfile_data = ''
    while True:
        response = client.download_db_log_file_portion(
            DBInstanceIdentifier=instance_name,
            LogFileName=logfile_name, Marker=next_position_marker)
        if 'LogFileData' not in response:
            logger.error('no LogFileData in logfile portion response.\n{}'.format(
                json.dumps(response)))
        fh.write(response['LogFileData'])
        if not response['AdditionalDataPending']:
            break
        next_position_marker = response['Marker']
    return 


def get_size(instance_name, logfile_name):
    for logfile in describe_logfiles_of_instance(instance_name):
        if logfile['LogFileName'] == logfile_name:
            return logfile['Size']
    return
