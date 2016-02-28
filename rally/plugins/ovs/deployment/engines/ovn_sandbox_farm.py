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
from ...consts import ResourceType


from sandbox import SandboxEngine
from netaddr.ip import IPRange


LOG = logging.getLogger(__name__)

@engine.configure(name="OvnSandboxFarmEngine", namespace="ovs")
class OvnSandboxFarmEngine(SandboxEngine):
    """ Deploy ovn sandbox controller

    Sample configuration:

    {
        "type": "OvnSandboxFarmEngine",
        "deployment_name": "ovn-sandbox-node-0",
        "ovs_repo" : "https://github.com/openvswitch/ovs.git",
        "ovs_branch" : "branch-2.5",
        "ovs_user" : "rally",
        "provider": {
            "type": "OvsSandboxProvider",
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
            "deployment_name": {"type": "string"},
            "http_proxy": {"type": "string"},
            "https_proxy": {"type": "string"},
            "ovs_repo": {"type": "string"},
            "ovs_user": {"type": "string"},
            "ovs_branch": {"type": "string"},
            "provider": {"type": "object"},
        },
        "required": ["type", "provider"]
    }


    def __init__(self, deployment):
        super(OvnSandboxFarmEngine, self).__init__(deployment)



    def validate(self):
        super(OvnSandboxFarmEngine, self).validate()


    @logging.log_deploy_wrapper(LOG.info, _("Deploy ovn sandbox farm"))
    def deploy(self):
        self.servers = self.get_provider().create_servers()

        server = self.servers[0]
        dep_name = self.deployment["name"]
        LOG.info("Deploy farm node %s" % dep_name)
        self._deploy(server)

        ovs_user = self.config.get("ovs_user", OVS_USER)
        credential = server.get_credentials()
        credential["user"] = ovs_user

        self.deployment.add_resource(provider_name="OvnSandboxFarmEngine",
                                 type=ResourceType.CREDENTIAL,
                                 info=credential)


        self.deployment.add_resource(dep_name,
                             ResourceType.SANDBOXES,
                             info={"farm": dep_name, "sandboxes": []})

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

