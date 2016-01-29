#
# Created on Jan 29, 2016
#
# @author: lhuang8
#

import copy

from rally.common.i18n import _ 
from rally.common import logging
from rally.common import db
from rally.common import objects
from rally import consts
from rally.task import context
from ..consts import ResourceType
from .. import utils  

LOG = logging.getLogger(__name__)



def get_ovn_multihost_info(deploy_uuid, controller_name):
    
    deployments = db.deployment_list(parent_uuid=deploy_uuid)
    
    multihost_info = {"controller" : {}, "farms" : {} }
    
    
    for dep in deployments:
        
        cred = db.resource_get_all(dep["uuid"], type=ResourceType.CREDENTIAL)[0]
        cred = copy.deepcopy(cred.info)
        name = dep["name"]
        
        info = { "name" : name, "credential" :  cred}
        
        if name == controller_name:
            multihost_info["controller"][name] = info
        else:
            multihost_info["farms"][name] = info
    
    return multihost_info


@context.configure(name="ovn_multihost", order=110)
class OvnMultihost(context.Context):
    
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "properties": {
        },
        "additionalProperties": True
    }
    
    DEFAULT_CONFIG = {
    }
    
    @logging.log_task_wrapper(LOG.info, _("Enter context: `ovn_controller`"))
    def setup(self):
        
        multihost_uuid = self.task["deployment_uuid"]
        controller_name = self.config["controller"]
        
        multihost_info = get_ovn_multihost_info(multihost_uuid, controller_name)
        self.context["ovn_multihost"] = multihost_info
        
        
    @logging.log_task_wrapper(LOG.info, _("Exit context: `network`"))
    def cleanup(self):
        pass
        
        
    
    