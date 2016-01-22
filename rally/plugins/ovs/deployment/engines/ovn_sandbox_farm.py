#
# Created on Jan 21, 2016
#
# @author: lhuang8
#

import os
import sys
import netaddr
import six
from six.moves.urllib import parse
import subprocess


from rally.common.i18n import _
from rally.common import logging
from rally.common import objects
from rally import consts
from rally import exceptions
from rally.deployment import engine # XXX: need a ovs one?
from rally.deployment.serverprovider import provider


from . import get_script
from . import get_updated_server
from . import OVS_USER

from sandbox import SandboxEngine
from netaddr.ip import IPRange


LOG = logging.getLogger(__name__)

@engine.configure(name="OvnSandboxFarmEngine", namespace="ovs")
class OvnSandboxFarmEngine(SandboxEngine):
    """ Deploy ovn sandbox controller 
    
    Sample configuration:

    {
        "type": "OvnSandboxFarmEngine",
        "ovs_repo" : "https://github.com/openvswitch/ovs.git",
        "ovs_branch" : "branch-2.5",
        "ovs_user" : "rally",
        "amount": 2,
        "start_network": "192.168.20.20/24",
        "net_dev": "eth1",
        "controller_ip": "192.168.20.10",
        "provider": {
            "type": "OvsSandboxProvider",
            "deployment_name": "OVN sandbox farm 1",
            "credentials": [
                {
                    "host": "192.168.20.20",
                    "user": "root"}
            ]
        }
    }
    
    """
    
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "ovs_repo": {"type": "string"},
            "ovs_user": {"type": "string"},
            "ovs_branch": {"type": "string"},
            "amount" : {"type": "integer"},
            "start_network": {"type": "string",
                                "pattern": "^(\d+\.){3}\d+\/\d+$"},
            "controller_ip": {"type": "string",
                               "pattern": "^(\d+\.){3}\d+$"},
            "provider": {"type": "object"},
        },
        "required": ["type", "provider"]
    }
    
    
    def __init__(self, deployment):
        super(OvnSandboxFarmEngine, self).__init__(deployment)
       

    
    def validate(self):
        super(OvnSandboxFarmEngine, self).validate()
        
        if "start_network" not in self.config:
            return
        
        sandbox_net = netaddr.IPNetwork(self.config["start_network"])
        sandbox_amount = self.config.get("amount", 1)
        
        ip_range = IPRange(sandbox_net.ip, sandbox_net.last)
        sandbox_net_size = ip_range.last - ip_range.first
        
        
        if  sandbox_net_size < sandbox_amount:
            message = _("Network %s size is not big enough for %d hosts.")
            raise exceptions.InvalidConfigException(
                        message % (sandbox_net, sandbox_amount))
        

    @logging.log_deploy_wrapper(LOG.info, _("Deploy ovn sandbox farm"))
    def deploy(self):
        self.servers = self.get_provider().create_servers()
        
        server = self.servers[0] 
        
        self._prepare_server(server)
        
        #TODO: add sandbox info to resource
        self.deployment.add_resource(provider_name="OvnSandboxFarmEngine",
                                 type="credentials",
                                 info=server.get_credentials())
        
  
        ovs_user = self.config.get("ovs_user", OVS_USER)
        amount = self.config.get("amount", 1)
        
        ovs_server = get_updated_server(server, user=ovs_user)
        controller_ip = self.config.get("controller_ip")
        start_network = self.config.get("start_network")
        net_dev = self.config.get("net_dev", "eth0")
        
        
        sandbox_network = netaddr.IPNetwork(start_network) 
        sandbox_hosts = sandbox_network.iter_hosts()
        

        if controller_ip == None:
            raise exceptions.NoSuchConfigField(name="controller_ip")


        sandbox_hosts = netaddr.iter_iprange(sandbox_network.ip, 
                                            sandbox_network.last)
        for i in range(amount):
            farm_host_ip = str(sandbox_hosts.next())
            cmd = "/bin/bash -s - --ovn --controller-ip %s \
                --host-ip %s/%d --device %s --index %d" % \
                (controller_ip, farm_host_ip, sandbox_network.prefixlen,
                 net_dev, i)
            
            
            ovs_server.ssh.run(cmd, stdin=get_script("ovs-sandbox-deploy.sh"),
                                stdout=sys.stdout, stderr=sys.stderr);
            
        credential = objects.Credential(server.host, 
                            server.user, server.password)
        
        
        return {"admin": credential}
        
        
        
        
    def cleanup(self):    
        """Cleanup OVN deployment."""
        
