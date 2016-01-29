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
#from rally.cli.ovs_commands import task
#from rally.cli.commands import deployment
from rally.cli.commands import task

from rally.common import profile

profile.profile = profile.PROFILE_OVS

ovs_categories = {
    "deployment": deployment.DeploymentCommands,
    "task": task.TaskCommands,
}



def main():
    return cliutils.run(sys.argv, ovs_categories)


if __name__ == '__main__':
    sys.exit(main())
