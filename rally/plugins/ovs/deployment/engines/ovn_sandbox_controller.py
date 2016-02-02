#
# Created on Jan 21, 2016
#
# @author: lhuang8
#

import os
import sys
import six
from six.moves.urllib import parse
import subprocess


from rally.common.i18n import _
from rally.common import logging
from rally.common import objects
from rally import consts
from rally.deployment import engine # XXX: need a ovs one?
from rally.deployment.serverprovider import provider


from . import get_script
from . import get_updated_server
from . import OVS_USER
from ...consts import ResourceType


from sandbox import SandboxEngine


LOG = logging.getLogger(__name__)

@engine.configure(name="OvnSandboxControllerEngine", namespace="ovs")
class OvnSandboxControllerEngine(SandboxEngine):
    """ Deploy ovn sandbox controller 
    
    Sample configuration:

    {
        "type": "OvnSandboxControllerEngine",
        "deployment_name": "ovn-controller-node",
        "ovs_repo": "https://github.com/openvswitch/ovs.git",
        "ovs_branch": "branch-2.5",
        "ovs_user": "rally",
        "net_dev": "eth1",
        "controller_cidr": "192.168.10.10/16",
        "provider": {
            "type": "OvsSandboxProvider",
            "credentials": [
                {
                    "host": "192.168.20.10",
                    "user": "root"}
            ]
        }
    }
    
    """
    
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "deployment_name": {"type": "string"},
            "http_proxy": {"type": "string"},
            "https_proxy": {"type": "string"},
            "ovs_repo": {"type": "string"},
            "ovs_branch": {"type": "string"},
            "ovs_user": {"type": "string"},
            "net_dev": {"type": "string"},
            "controller_cidr": {"type": "string",
                                "pattern": "^(\d+\.){3}\d+\/\d+$"},
            "provider": {"type": "object"},
        },
        "required": ["type", "controller_cidr", "provider"]
    }
    def __init__(self, deployment):
        super(OvnSandboxControllerEngine, self).__init__(deployment)
        

    
    

    @logging.log_deploy_wrapper(LOG.info, _("Deploy ovn sandbox controller"))
    def deploy(self):
        self.servers = self.get_provider().create_servers()
        
        server = self.servers[0]# only support to deploy controller node
                                # on one server  
        
        self._deploy(server)
        
        deployment_name = self.deployment["name"]
        if not deployment_name:
            deployment_name = self.config.get("deployment_name", None)
        
        ovs_user = self.config.get("ovs_user", OVS_USER)
        ovs_controller_cidr = self.config.get("controller_cidr")
        net_dev = self.config.get("net_dev", "eth0")
        

        # start ovn controller with non-root user
        ovs_server = get_updated_server(server, user=ovs_user)
           
        cmd = "./ovs-sandbox.sh --controller --ovn \
                            --controller-ip %s --device %s;" % \
                        (ovs_controller_cidr, net_dev)
        
        ovs_server.ssh.run(cmd,
                            stdout=sys.stdout, stderr=sys.stderr)

        self.deployment.add_resource(provider_name="OvnSandboxControllerEngine",
                                 type=ResourceType.CREDENTIAL,
                                 info=ovs_server.get_credentials())
        
        self.deployment.add_resource(provider_name="OvnSandboxControllerEngine",
                            type=ResourceType.CONTROLLER,
                            info={
                                  "ip":ovs_controller_cidr.split('/')[0],
                                  "deployment_name":deployment_name})
        
        
        return {"admin": None}
        
    def cleanup(self):
        """Cleanup OVN deployment."""
        for resource in self.deployment.get_resources():
            if resource["type"] == ResourceType.CREDENTIAL:
                server = provider.Server.from_credentials(resource.info)

                cmd = "[ -x ovs-sandbox.sh ] && ./ovs-sandbox.sh --cleanup"

                server.ssh.run(cmd,
                            stdout=sys.stdout, stderr=sys.stderr,
                            raise_on_error=False)

            self.deployment.delete_resource(resource.id)



        
