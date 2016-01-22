#
# Created on Jan 16, 2016
#
# @author: lhuang8
#


""" CLI interface for Rally OVS. """
from __future__ import print_function


import sys

from rally.cli import cliutils
from rally.cli.ovs_commands import deployment


ovs_categories = {
    "deployment": deployment.OVSDeploymentcommands,
}



def main():
    return cliutils.run(sys.argv, ovs_categories)


if __name__ == '__main__':
    sys.exit(main())
