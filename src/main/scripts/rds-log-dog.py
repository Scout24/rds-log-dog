#!/usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals, division
from rds_log_dog.main import Main

def lambda_handler(event, context):
    main = Main()
    return main.do()

if __name__ == "__main__":
     print("local mode executing ...")
     main = Main()
     main.do()

