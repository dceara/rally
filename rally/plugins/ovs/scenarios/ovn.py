#
# Created on Jan 25, 2016
#
# @author: lhuang8
#


from rally.plugins.ovs import scenario
from rally.task import atomic



class OvnScenario(scenario.OvsScenario):
    
    
    RESOURCE_NAME_FORMAT = "lswitch_XXXXXX_XXXXXX"
    
    @atomic.action_timer("ovn.create_lswitch")
    def _create_lswitch(self, lswitch_create_args):
        
        print("create lswitch")
        self.RESOURCE_NAME_FORMAT = "lswitch_XXXXXX_XXXXXX"
        
        amount = lswitch_create_args.get("amount", 1)
        
        ovn_nbctl = self.controller_client("ovn-nbctl")
        ovn_nbctl.set_sandbox("controller-sandbox")
        
        lswitches = []
        
        for i in range(amount):
            
            name = self.generate_random_name()
            
            lswitch = ovn_nbctl.lswitch_add(name)
            lswitches.append(lswitch)
            
        return lswitches
            
        
    @atomic.optional_action_timer("neutron.list_lswitch")
    def _list_lswitches(self):
        print("list lswitch")
        ovn_nbctl = self.controller_client("ovn-nbctl")
        ovn_nbctl.set_sandbox("controller-sandbox")
        ovn_nbctl.lswitch_list()
    
    @atomic.action_timer("ovn.delete_lswitch")
    def _delete_lswitch(self, lswitches):
        print("delete lswitch")
        ovn_nbctl = self.controller_client("ovn-nbctl")
        ovn_nbctl.set_sandbox("controller-sandbox")

        for lswitch in lswitches:
            ovn_nbctl.lswitch_del(lswitch["name"])
        
    
    
    def _get_or_create_lswitch(self, lswitch_create_args=None):
        pass
    
    
    
    
    @atomic.action_timer("ovn.create_lport")
    def _create_lport(self, lswitch, lport_create_args, lport_amount=1):
        print("create lport")
        ovn_nbctl = self.controller_client("ovn-nbctl")
        ovn_nbctl.set_sandbox("controller-sandbox")
        
        self.RESOURCE_NAME_FORMAT = "lport_XXXXXX_XXXXXX"
        lports = []
        for i in range(lport_amount):
            name = self.generate_random_name()
            lport = ovn_nbctl.lport_add(lswitch["name"], name)
            lports.append(lport)
        
        return lports
    
    @atomic.action_timer("ovn.delete_lport")
    def _delete_lport(self, lports):
        print("delete lport")
        ovn_nbctl = self.controller_client("ovn-nbctl")
        ovn_nbctl.set_sandbox("controller-sandbox")

        for lport in lports:
            ovn_nbctl.lport_del(lport["name"])
    
    
    
    @atomic.action_timer("ovn.action_timer")
    def _list_lports(self, lswitches):
        print("list lports")
        ovn_nbctl = self.controller_client("ovn-nbctl")
        ovn_nbctl.set_sandbox("controller-sandbox")
        for lswitch in lswitches:
            ovn_nbctl.lport_list(lswitch["name"])
        
        
        
    
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







