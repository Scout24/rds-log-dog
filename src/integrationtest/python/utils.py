from __future__ import print_function, absolute_import, unicode_literals, division

from rds_log_dog.discoverer import Discoverer


def get_one_rds_instance():
    disco = Discoverer()
    instances = disco.discover()
    assert (0 < len(instances)), "We need at least one RDS instance for this test!"
    # pick one instance
    return instances.pop()
