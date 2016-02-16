#
# Created on Jan 25, 2016
#
# @author: lhuang8
#
 




from rally.plugins.ovs.scenarios import ovn

from rally.task import scenario
from rally.task import validation

class OvnNorthbound(ovn.OvnScenario):
    """Benchmark scenarios for OVN northbound."""
    
    @scenario.configure(context={})
    def create_and_list_lswitch(self, lswitch_create_args=None):
        self._create_lswitch(lswitch_create_args)
        self._list_lswitches()
        

    @scenario.configure(context={})
    def create_and_delete_lswitch(self, lswitch_create_args=None): 
        lswitches = self._create_lswitch(lswitch_create_args or {})
        self._delete_lswitch(lswitches)
        
        
        
    @validation.number("lports_per_lswitch", minval=1, integer_only=True)    
    @scenario.configure(context={})
    def create_and_list_lport(self, 
                              lswitch_create_args=None,
                              lport_create_args=None,
                              lports_per_lswitch=None):
        
        lswitches = self._create_lswitch(lswitch_create_args)
        
        for lswitch in lswitches:
            self._create_lport(lswitch, lport_create_args, lports_per_lswitch)
        
        self._list_lports(lswitches)
    

    @scenario.configure(context={})
    def create_and_delete_lport(self,
                              lswitch_create_args=None,
                              lport_create_args=None,
                              lports_per_lswitch=None):
        
        lswitches = self._create_lswitch(lswitch_create_args)
        for lswitch in lswitches:
            lports = self._create_lport(lswitch, lport_create_args,
                                        lports_per_lswitch)
            self._delete_lport(lports)
        
        self._delete_lswitch(lswitches)
        
        
        