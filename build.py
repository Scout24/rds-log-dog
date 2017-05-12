import os

from pybuilder.core import use_plugin, init
from pybuilder.vcs import VCSRevision

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('pypi:pybuilder_aws_plugin')
use_plugin('python.integrationtest')
use_plugin('python.pytddmon')
use_plugin("filter_resources")

name = "rds_log_dog"
url = 'https://github.com/ImmobilienScout24/rds-log-dog'
description = open("README.md").read()
license = 'MIT'
version = '0.2.{}'.format(VCSRevision().get_git_revision_count())

default_task = ["analyze", "package"]

@init
def set_properties(project):
    project.build_depends_on('unittest2>=0.7')
    # needed until moto>=0.4.32 is released
    project.build_depends_on('git+https://github.com/spulec/moto.git@master#egg=moto')
    project.build_depends_on('mock')
    project.depends_on('boto3')

    project.set_property('bucket_prefix', 'dist/')
    project.version = '%s.%s' % (project.version, os.environ.get('BUILD_NUMBER', 0))

    project.set_property("coverage_break_build", True)
    project.set_property("integrationtest_inherit_environment", True)
    project.set_property("integrationtest_parallel", True)

    project.get_property('filter_resources_glob').extend(['**/rds_log_dog/__init__.py'])
