#
# Created on Jan 27, 2016
#
# @author: lhuang8
#


from rally.common import logging
from rally import consts
from rally.task import context

LOG = logging.getLogger(__name__)




@context.configure(name="ovn_sandbox", order=110)
class OvnSandbox(context.Context):
    """Context for xxxxx."""
    
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "properties": {
            "foo": {
                "type": "integer",
                "minimum": 1
            }
        },
        "additionalProperties": True
    }
    
    DEFAULT_CONFIG = {
        "foo": 1
    }
    
    
    def setup(self):
        """Create Fuel environments, using the broker pattern."""
        
        LOG.debug("Setup ovn sandbox context")

    def cleanup(self):
        LOG.debug("Cleanup ovn sandbox context")
    
    