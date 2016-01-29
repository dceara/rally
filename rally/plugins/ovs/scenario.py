#
# Created on Jan 25, 2016
#
# @author: lhuang8
#


import six

from rally.task import scenario
from rally.common import db
from rally.common import objects
from rally.common import sshutils

from rally.deployment.serverprovider import provider
import itertools

from consts import ResourceType

from utils import *


class OvsScenario(scenario.Scenario):
    """Base class for all OVS scenarios."""
    
    
    
    def __init__(self, context=None, clients=None):
        super(OvsScenario, self).__init__(context)
        
        multihost_info = context["ovn_multihost"]
        
        for k,v in six.iteritems(multihost_info["controller"]):
            cred = v["credential"]
            self._controller_client = get_ssh_from_credential(cred)
            
        
        self._farm_clients = {}
        for k,v in six.iteritems(multihost_info["farms"]):
            cred = v["credential"]
            ssh = get_ssh_from_credential(cred)
            self._farm_clients[k] = ssh
        
    
    def controller_client(self, client_type=None):
        return self._controller_client
    
    
    def farm_clients(self, name, client_type=None):
        return self._farm_clients[name]
    

    










