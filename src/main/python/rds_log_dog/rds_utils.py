from __future__ import print_function, absolute_import, division

import logging
import time
import boto3

logger = logging.getLogger(__name__)


_DEBUG_TOTAL_WRITTEN_BYTES = 0


def describe_logfiles_of_instance(name):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    response = client.describe_db_log_files(
        DBInstanceIdentifier=name)
    if 'DescribeDBLogFiles' in response:
        return response['DescribeDBLogFiles']
    return []


def metric(name, value=1):
    # DogStatsD format (https://www.datadoghq.com/blog/statsd/)
    # MONITORING|unix_epoch_timestamp|metric_value|metric_type|my.metric.name|#tag1:value,tag2
    print('MONITORING|{ts}|{value}|{type}|rds_log_dog.{name}|'.format(
        ts=int(time.time()), type='count', name=name, value=value))


def download(instance_name, logfile_name, filename):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    next_position_marker = '0'
    data = ''
    retries = 0
    max_retries = 3
    size = 0
    fetch_this_number_of_lines = 0
    with open(filename, 'w') as datafile:
        while True:
            if retries > max_retries:
                metric('retries_exceeded')
                logger.error(
                    'Retry count (%d) exceeding max retries (%d). Gave up.',
                    retries, max_retries)
                break
            response = client.download_db_log_file_portion(
                DBInstanceIdentifier=instance_name,
                LogFileName=logfile_name, Marker=next_position_marker,
                NumberOfLines=fetch_this_number_of_lines)
            if 'LogFileData' not in response:
                logger.warn('no LogFileData in response. Retrying.')
                retries += 1
                continue  # means retry
            data = response['LogFileData']
            if data[-35:].strip().endswith('[Your log message was truncated]'):
                metric('truncated')
                fetch_this_number_of_lines = data.count('\n')-2
                retries += 1
                continue  # means retry
            logger.debug('going to write %d bytes to disc.\
                Already written: %d bytes', len(data), size)
            datafile.write(data)
            size += len(data)
            global _DEBUG_TOTAL_WRITTEN_BYTES
            _DEBUG_TOTAL_WRITTEN_BYTES += len(data)
            if not response['AdditionalDataPending']:
                break
            next_position_marker = response['Marker']
            fetch_this_number_of_lines = 0
            retries = 0
    metric('rds_log_size', size)


def get_size(instance_name, logfile_name):
    for logfile in describe_logfiles_of_instance(instance_name):
        if logfile['LogFileName'] == logfile_name:
            return logfile['Size']
