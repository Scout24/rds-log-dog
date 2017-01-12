from __future__ import print_function, absolute_import, division

import subprocess
from subprocess import Popen, PIPE

def execute_command(cmd, timeout=None):
    if timeout:
        cmd = 'timeout {0} {1}'.format(timeout, cmd)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return (p.returncode, stdout, stderr)

def do():
    cmd = "aws s3 ls"
    rc, stdout, stderr = execute_command(cmd)

    type(stdout)
    print("rc: ", rc)
    print("output: ", stdout)
    print("error: ", stderr)
    print("--")

if __name__ == "__main__":
    do()

