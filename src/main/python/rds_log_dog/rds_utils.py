import boto3


def describe_logfiles_of_instance(name):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    response = client.describe_db_log_files(
        DBInstanceIdentifier=name)
    if 'DescribeDBLogFiles' in response:
        return response['DescribeDBLogFiles']
    return []


def get_full_db_logfile_data(instance_name, logfile_name):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    next_position_marker = '0'
    logfile_data = ''
    while True:
        response = client.download_db_log_file_portion(
            DBInstanceIdentifier=instance_name,
            LogFileName=logfile_name, Marker=next_position_marker)
        if not 'LogFileData' in response:
            logger.error('no LogFileData in logfile portion response.\n{}'.format(
                json.dumps(response)))
        logfile_data += response['LogFileData']
        if not response['AdditionalDataPending']:
            break
        next_position_marker = response['Marker']
    return logfile_data
