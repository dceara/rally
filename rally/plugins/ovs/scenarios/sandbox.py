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
        batch = sandbox_create_args.get("batch", 1)
        
        farm = sandbox_create_args.get("farm")
        controller_ip = self.context["controller"]["ip"]
        
        start_cidr = sandbox_create_args.get("start_cidr")
        net_dev = sandbox_create_args.get("net_dev", "eth0")
        
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
        
        batch_left = min(batch, amount)
        i = 0
        while i < amount:
            
            i += batch_left
            host_ip_list = []
            while batch_left > 0:
                host_ip_list.append(str(sandbox_hosts.next()))
                batch_left -= 1
            
            cmds = []
            for host_ip in host_ip_list:
                cmd = "./ovs-sandbox.sh --ovn --controller-ip %s \
                             --host-ip %s/%d --device %s" % \
                         (controller_ip, host_ip, sandbox_cidr.prefixlen,
                                net_dev)
                cmds.append(cmd)
        
            ssh.run(";".join(cmds),
                                stdout=sys.stdout, stderr=sys.stderr);
        
            batch_left = min(batch, amount - i)
            if batch_left <= 0:
                break;
    
    @atomic.action_timer("sandbox.delete_sandbox")
    def _delete_sandbox(self, sandbox):
        print("delete sandbox")
        pass
    




