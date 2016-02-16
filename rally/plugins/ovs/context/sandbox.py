#
# Created on Jan 27, 2016
#
# @author: lhuang8
#

import copy
from rally.common.i18n import _ 
from rally.common import logging
from rally.common import db
from rally import consts
from rally.task import context

from ..consts import ResourceType

LOG = logging.getLogger(__name__)




@context.configure(name="sandbox", order=110)
class Sandbox(context.Context):
    """Context for xxxxx."""
    
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "properties": {
        },
        "additionalProperties": True
    }
    
    DEFAULT_CONFIG = {
    }
    
    @logging.log_task_wrapper(LOG.info, _("Enter context: `sandbox`"))
    def setup(self):
        
        LOG.debug("Setup ovn sandbox context")
        deploy_uuid = self.task["deployment_uuid"]
        deployments = db.deployment_list(parent_uuid=deploy_uuid)
        
        
        sandboxes = []
        for dep in deployments:
            res = db.resource_get_all(dep["uuid"], type=ResourceType.SANDBOXES)
            if len(res) == 0: 
                continue
            
            info = copy.deepcopy(res[0].info)
            sandboxes.append(info)

            
        self.context["sandboxes"] = sandboxes    
        

    def cleanup(self):
        LOG.debug("Cleanup ovn sandbox context")
    
    