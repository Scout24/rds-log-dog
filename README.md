rds-log-dog
===========

rds-log-dog is a tool to automatically feed your [https://aws.amazon.com/de/rds/](AWS RDS) logfiles into your monitoring solutions.
It should reduce the manual effort in accessing the log files from your RDS intances.
You can now define, how long you want to store your database logfiles (in s3).


## rds-log-dog is currently under development and not yet ready for production use. ##

How does it work?
=================

Overview
--------

The logfiles of your AWS RDS instances will be automatically stored in a s3 bucket (default starts with: rds-log-dog).
From there you can feed the logfiles into you kibana or other monitoring/logging solutions.


How to install it?
================
Run the script: deploy_all.sh

How do I use it?
================


How to contribute ?
===================

Clone the project with: 

    git clone git@github.com:ImmobilienScout24/rds-log-dog.git

We recommend installing PyBuilder in a [virtual environment](https://virtualenv.pypa.io/en/stable/):

    pip install virtualenv
    cd rds-log-dog
    virtualenv .venv
    source .venv/bin/activate

Install pybuilder & dependencies:
    pip install pybuilder
    pyb install_dependencies

Now you can build and run tests with:
    pyb 

