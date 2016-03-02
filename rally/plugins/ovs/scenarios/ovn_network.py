#
# Created on Feb 15, 2016
#
# @author: lhuang8
#


import random

from rally.common import logging
from rally.plugins.ovs.scenarios import ovn

from rally.task import scenario
from rally.task import validation
from ..utils import get_random_mac

LOG = logging.getLogger(__name__)



class OvnNetwork(ovn.OvnScenario):
    """scenarios for OVN network."""




    @validation.number("ports_per_network", minval=1, integer_only=True)
    @scenario.configure(context={})
    def create_and_bind_ports(self,
                              network_create_args=None,
                              port_create_args=None,
                              ports_per_network=None):

        wait_up = port_create_args.get("wait_up", False)
        sandboxes = []

        for i in self.context["sandboxes"]:
            if len(i["sandboxes"]) < 1:
                continue
            sandboxes += [i]

        lswitches = self._create_lswitch(network_create_args)
        for lswitch in lswitches:
            lports = self._create_lport(lswitch, port_create_args, ports_per_network)
            self._bind_port(lports, sandboxes, wait_up)


    def bind_ports(self):
        pass

    def bind_and_unbind_ports(self):
        pass


