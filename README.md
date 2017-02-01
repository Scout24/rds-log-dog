rds-log-dog
===========

rds-log-dog is a tool to automatically feed your [AWS RDS](https://aws.amazon.com/de/rds/) logfiles into your monitoring solutions.
It should reduce the manual effort in accessing the log files from your RDS intances.
You can now define, how long you want to store your database logfiles (in s3).


rds-log-dog is in the early stage of development. 

How does it work?
=================

Overview
--------

The logfiles of your AWS RDS instances will be automatically stored in a s3 bucket (default starts with: rds-log-dog).
From there you can feed the logfiles into you ELK stack or other monitoring/logging solutions.


How to install it?
================

Run the script, there will be a help: 

    ./deploy.sh

If you want to install or update the infrastructure (policies, s3 bucket) and the lambda code, run:

    ./deploy.sh -icp

How do I use it?
================


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

Running integration tests:

    pyb run_integration_tests

For the tests you need the some variables from the deploy.sh in target/. So first run ./deploy.sh. 

License
=======

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

