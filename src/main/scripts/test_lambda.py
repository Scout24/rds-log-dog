""" when running in the AWS console, you can use event to give in some arguments.
e.g.: extend hello  to: hello ( event['name'] )

until now we don't use it here.
"""

from rds_log_dog import hello

def handler(event, context):
    print hello()
