#
# Created on Jan 25, 2016
#
# @author: lhuang8
#
 




from rally.plugins.ovs.scenarios import ovn

from rally.task import scenario


class OvnNorthbound(ovn.OvnScenario):
    """Benchmark scenarios for OVN northbound."""
    
    @scenario.configure(context={})
    def create_and_list_lswitch(self, lswitch_create_args=None):
        self._create_lswitch(lswitch_create_args)
        self._list_lswitch()
        
        
    @scenario.configure(context={})
    def create_and_list_lport(self, 
                              lswitch_create_args=None,
                              lport_create_args=None):
        
        lswitch = self._get_or_create_lswitch(lswitch_create_args)
        self._create_lport(lswitch, lport_create_args)
        
        
    

