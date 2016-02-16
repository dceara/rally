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


    def _deploy_node(self, config, name):
        deployment = objects.Deployment(config=config,
                                        parent_uuid=self.deployment["uuid"])
        deployment.update_name(name)
        deployer = engine.Engine.get_engine(config["type"], deployment)
        with deployer:
            credentials = deployer.make_deploy()
        return deployer, credentials


    
    def deploy(self):
        self.deployment.update_status(consts._DeployStatus.DEPLOY_SUBDEPLOY)
        
        controller_config = self.config["controller"]
        name = controller_config.get("deployment_name",  
                                     "%s-controller" % self.deployment["name"])
        self.controller, self.credentials = self._deploy_node(
                    controller_config, name)
    
        
        if "nodes" in self.config:
            for i in range(len(self.config["nodes"])):
                node_config = self.config["nodes"][i]
                
                name = node_config.get("deployment_name", 
                            "%s-node-%d" % (self.deployment["name"], i))
                node, credential = self._deploy_node(node_config, name)
                self.nodes.append(node)
        
        return self.credentials        
    
    
    def cleanup(self):
        subdeploys = db.deployment_list(parent_uuid=self.deployment["uuid"])
        for subdeploy in subdeploys:
            rally.api.Deployment.destroy(subdeploy["uuid"])
