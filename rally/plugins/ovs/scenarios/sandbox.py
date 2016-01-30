#
# Created on Jan 28, 2016
#
# @author: lhuang8
#

import sys
import netaddr

from rally import exceptions
from rally.plugins.ovs import scenario
from rally.task import atomic

from rally.common import objects

from ..deployment.engines import get_script 
from netaddr.ip import IPRange

class SandboxScenario(scenario.OvsScenario):
    
    
    @atomic.action_timer("sandbox.create_sandbox")
    def _create_sandbox(self, sandbox_create_args):
        """
        :param sandbox_create_args from task config file
        """
        
        print("create sandbox")
                
        amount = sandbox_create_args.get("amount", 1)
        
        farm = sandbox_create_args.get("farm")
        # xxx: get controller_ip from resources table
        controller_ip = sandbox_create_args.get("controller_ip") 
        start_cidr = sandbox_create_args.get("start_cidr")
        net_dev = sandbox_create_args.get("net_dev", "eth0")
        # xxx: check start_cidr and controller_ip in same network
        
        if controller_ip == None:
            raise exceptions.NoSuchConfigField(name="controller_ip")
        
        sandbox_cidr = netaddr.IPNetwork(start_cidr) 
        end_ip = sandbox_cidr.ip + amount
        if not end_ip in sandbox_cidr:
            message = _("Network %s's size is not big enough for %d sandboxes.")
            raise exceptions.InvalidConfigException(
                        message  % (start_cidr, amount))
        
        
        sandbox_hosts = netaddr.iter_iprange(sandbox_cidr.ip, sandbox_cidr.last)
        
        ssh = self.farm_clients(farm)
        
        for i in range(amount):
            farm_host_ip = str(sandbox_hosts.next())
            cmd = "/bin/bash -s - --ovn --controller-ip %s \
                --host-ip %s/%d --device %s --index %d" % \
                (controller_ip, farm_host_ip, sandbox_cidr.prefixlen,
                 net_dev, i)
        
            ssh.run(cmd, stdin=get_script("ovs-sandbox.sh"),
                                stdout=sys.stdout, stderr=sys.stderr);
        
    
    @atomic.action_timer("sandbox.delete_sandbox")
    def _delete_sandbox(self, sandbox):
        print("delete sandbox")
        pass
    




