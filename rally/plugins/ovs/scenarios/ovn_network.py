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



def get_random_sandbox(sandboxes):
    info = random.choice(sandboxes)
    sandbox = random.choice(info["sandboxes"])

    return info["farm"], sandbox

class OvnNetwork(ovn.OvnScenario):
    """scenarios for OVN network."""




    @validation.number("ports_per_network", minval=1, integer_only=True)
    @scenario.configure(context={})
    def create_and_bind_ports(self,
                              network_create_args=None,
                              port_create_args=None,
                              ports_per_network=None):

        lswitches = self._create_lswitch(network_create_args)
        lports = []

        for lswitch in lswitches:
            lports += self._create_lport(lswitch, port_create_args, ports_per_network)

        sandbox_info = self.context["sandboxes"]


        for lport in lports:
            farm, sandbox = get_random_sandbox(sandbox_info)
            port_name = lport["name"]

            LOG.debug("bind %s to %s on %s" % (port_name, sandbox, farm))

            ovs_vsctl = self.farm_clients(farm, "ovs-vsctl")
            ovs_vsctl.set_sandbox(sandbox)
            ovs_vsctl.enable_batch_mode()

            ovs_vsctl.add_port('br-int', port_name)
            ovs_vsctl.db_set('Interface', port_name,
                             ('external_ids', {"iface-id":port_name,
                                               "iface-status":"active"}),
                             ('admin_state', 'up'))

            ovs_vsctl.flush()
            # todo: wait port 'up' on northboud



