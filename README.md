rds_log_dog
===========

rds-log-dog is a tool to automatically feed your AWS RDS logfiles into your monitoring solutions.
It should reduce the manual effort in accesing the log files from your RDS intances.
You can now define, how long you want to store your database logfiles (in s3).


## rds-log-dog is currently under development and not yet ready for production use. ##

How does it work?
=================

Overview
--------

The logfiles of your AWS RDS instances will be automatically stored in a s3 bucket (default starts with: rds-log-dog).
From there you can feed the logfiles into you kibana or other monitoring/logging solutions.


How do I use it?
================

Run the script: deploy_all.sh

