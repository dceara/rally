#
# Created on Jan 25, 2016
#
# @author: lhuang8
#


from rally.plugins.ovs import scenario
from rally.task import atomic



class OvnScenario(scenario.OvsScenario):
    
    
    @atomic.action_timer("ovn.create_lswitch")
    def _create_lswitch(self, lswitch_create_args):
        pass
    
    @atomic.optional_action_timer("neutron.list_lswitch")
    def _list_lswitch(self):
        pass
    
    @atomic.action_timer("ovn.delete_lswitch")
    def _delete_lswitch(self):
        pass
    
    
    def _get_or_create_lswitch(self, lswitch_create_args=None):
        pass
    
    
    
    
    @atomic.action_timer("ovn.create_lport")
    def _create_lport(self, lswitch, lport_create_args):
        pass
    
    @atomic.action_timer("ovn.delete_lport")
    def _delete_lport(self):
        pass
    
    @atomic.action_timer("ovn.action_timer")
    def _list_lport(self):
        pass
    
    @atomic.action_timer("ovn.update_lport")
    def _update_lport(self):
        pass
    
    

    
    
    @atomic.action_timer("ovn.update_lswitch")
    def _update_lswitch(self):
        pass
    
    @atomic.action_timer("ovn.create_acl")
    def _create_acl(self):
        pass
    
    @atomic.action_timer("ovn.list_acl")
    def _list_acl(self):
        pass
    
    @atomic.action_timer("ovn.delete_acl")
    def _delete_acl(self):
        pass







