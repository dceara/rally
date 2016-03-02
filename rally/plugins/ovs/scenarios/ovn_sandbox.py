#
# Created on Jan 28, 2016
#
# @author: lhuang8
#

from rally.plugins.ovs.scenarios import sandbox

from rally.task import scenario
from rally.common import db
from rally.exceptions import NoSuchConfigField


class OvnSandbox(sandbox.SandboxScenario):

    @scenario.configure(context={})
    def create_controller(self, controller_create_args):
        multihost_dep = db.deployment_get(self.task["deployment_uuid"])

        config = multihost_dep["config"]
        controller_cidr = config["controller"].get("controller_cidr", None)
        net_dev = config["controller"].get("net_dev", None)
        deployment_name = config["controller"].get("deployment_name")

        controller_cidr = controller_create_args.get("controller_cidr",
                                                            controller_cidr)
        net_dev = controller_create_args.get("net_dev", net_dev)

        if controller_cidr == None:
            raise NoSuchConfigField(name="controller_cidr")

        if net_dev == None:
            raise NoSuchConfigField(name="net_dev")

        self._create_controller(deployment_name, controller_cidr, net_dev)



    @scenario.configure(context={})
    def create_sandbox(self, sandbox_create_args=None):
        self._create_sandbox(sandbox_create_args)


    @scenario.configure(context={})
    def create_and_delete_sandbox(self, sandbox_create_args=None):
        sandboxes = self._create_sandbox(sandbox_create_args)
        self.sleep_between(1, 2) # xxx: add min and max sleep args - l8huang
        self._delete_sandbox(sandboxes)

