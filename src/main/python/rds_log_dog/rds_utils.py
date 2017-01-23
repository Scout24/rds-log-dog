import boto3


def describe_logfiles_of_instance(name):  # pragma: no cover (covered by it)
    client = boto3.client('rds')
    response = client.describe_db_log_files(
        DBInstanceIdentifier=name)
    if 'DescribeDBLogFiles' in response:
        return response['DescribeDBLogFiles']
    return []