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

from sandbox import SandboxEngine


LOG = logging.getLogger(__name__)

@engine.configure(name="OvnSandboxControllerEngine", namespace="ovs")
class OvnSandboxControllerEngine(SandboxEngine):
    """ Deploy ovn sandbox controller 
    
    Sample configuration:

    {
        "type": "OvnSandboxControllerEngine",
        "provider": {
            "type": "OvsSandboxProvider",
            "deployment_name": "OVN controller node",
            "credentials": [
                {
                    "host": "192.168.20.10",
                    "user": "root"}
            ]
        }
    
    """
    
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "ovs_repo": {"type": "string"},
            "ovs_branch": {"type": "string"},
            "ovs_user": {"type": "string"},
            "provider": {"type": "object"},
        },
        "required": ["type", "provider"]
    }
    def __init__(self, deployment):
        super(OvnSandboxControllerEngine, self).__init__(deployment)
        


    @logging.log_deploy_wrapper(LOG.info, _("Deploy ovn sandbox controller"))
    def deploy(self):
        self.servers = self.get_provider().create_servers()
        
        server = self.servers[0]# only support to deploy controller node
                                # on one server  
        
        self._prepare_server(server)
        
        self.deployment.add_resource(provider_name="OvnSandboxControllerEngine",
                                 type="credentials",
                                 info=server.get_credentials())
        
  
        ovs_user = self.config.get("ovs_user", OVS_USER)
        
        ovs_server = get_updated_server(server, user=ovs_user)
        
        ovs_host_ip = server.host
        
        cmd = "/bin/bash -s - --controller --ovn --controller-ip %s" % \
                        (ovs_host_ip)
                        
        ovs_server.ssh.run("pwd", stdout=sys.stdout, stderr=sys.stderr);
                                        
        ovs_server.ssh.run(cmd, stdin=get_script("ovs-sandbox-deploy.sh"),
                            stdout=sys.stdout, stderr=sys.stderr);

        
        credential = objects.Credential(server.host, 
                            server.user, server.password)
        
        
        return {"admin": credential}
        
    def cleanup(self):    
        """Cleanup OVN deployment."""
        
