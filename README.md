rds-log-dog
===========

rds-log-dog is a tool to automatically feed your [AWS RDS](https://aws.amazon.com/de/rds/) logfiles into your monitoring solutions.
It should reduce the manual effort in accessing the log files from your RDS intances.
You can now define, how long you want to store your database logfiles (in s3).

After installing the tool, all your logfiles of your RDS instances (of one region) will be automatically fetched into a s3 bucket and stored around 30 days.

How does it work?
=================

Overview
--------

The logfiles of your AWS RDS instances will be automatically stored in a s3 bucket (default starts with: rds-log-dog).
From there you can feed the logfiles into you ELK stack or other monitoring/logging solutions.


How to install it?
================

Clone it:

     git clone git@github.com:ImmobilienScout24/rds-log-dog.git

Deploy to your AWS account with:

    ./deploy.sh -cis -p

You need the have aws credentials set in your bash session to deploy! If you set AWS_DEFAULT_REGION, this region will be used to deploy.

Now you have three cloudformation stacks:

- rds-log-dog-s3
- rds-log-dog-lambda
- rds-log-dog-scheduler


How do I use it?
================


After deploying with deploy.sh ...

All things are running automatically. You will find the logfiles of your RDS instances in a s3 bucket named like: 
   
    rds-log-dog-XXXXXXXXXXX

Alternativly you can collect the logfiles by calling the command line version of the tool:

    rds-log-dog.py


What does it cost ?
===================

With the default configuration and 4 instances with (together) 70MB of logfiles each hour, it will cost you appr. $1.30 per month.
Normal RDS installations have only some KB of logfiles and costs you some cents a month.

How to contribute ?
===================

You will need:

- jq
- python 2.7
- an AWS account

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

Now you can (locally) build and run tests with:

    pyb 

If you want to test it in your account, try to execute:

    ./deploy.sh -ci -v

This will deploy a personalized stack with your username (1st three chars).
And executing the integration tests.

Running integration tests seperately:

    pyb run_integration_tests

For the integration tests you need the some variables from the deploy.sh in target/. So first run ./deploy.sh. 


License
=======

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

