#
# Created on Jan 26, 2016
#
# @author: lhuang8
#

import six
from six.moves.urllib import parse

from rally.common import db
from rally.common import objects
from rally import consts
from rally.deployment import engine


import rally

@engine.configure(name="OvnMultihostEngine")
class OvnMultihostEngine(engine.Engine):
    """Deploy multihost cloud with existing engines.


    """    
    def __init__(self, *args, **kwargs):
        super(OvnMultihostEngine, self).__init__(*args, **kwargs)
        self.config = self.deployment["config"]
        self.nodes = []


    def _deploy_node(self, config):
        deployment = objects.Deployment(config=config,
                                        parent_uuid=self.deployment["uuid"])
        deployer = engine.Engine.get_engine(config["type"], deployment)
        with deployer:
            credentials = deployer.make_deploy()
        return deployer, credentials



    def _update_controller_ip(self, obj):
        if isinstance(obj, dict):
            keyval = six.iteritems(obj)
        elif isinstance(obj, list):
            keyval = enumerate(obj)

        for key, value in keyval:
            if isinstance(value, six.string_types):
                obj[key] = value.format(controller_ip=self.controller_ip)
            elif type(value) in (dict, list):
                self._update_controller_ip(value)
        


    
    def deploy(self):
        self.deployment.update_status(consts._DeployStatus.DEPLOY_SUBDEPLOY)
        self.controller, self.credentials = self._deploy_node(
                    self.config["controller"])
    
        credential = self.credentials["admin"]
        self.controller_ip = "" # TODO
        
        
        if "nodes" in self.config:
            for node_config in self.config["nodes"]:
                self._update_controller_ip(node_config)
                self.nodes.append(self._deploy_node(node_config)[0])
        
        return self.credentials        
    
    
    def cleanup(self):
        subdeploys = db.deployment_list(parent_uuid=self.deployment["uuid"])
        for subdeploy in subdeploys:
            rally.api.Deployment.destroy(subdeploy["uuid"])
