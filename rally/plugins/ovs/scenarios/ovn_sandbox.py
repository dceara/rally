#
# Created on Jan 28, 2016
#
# @author: lhuang8
#

from rally.plugins.ovs.scenarios import sandbox

from rally.task import scenario

class OvnSandbox(sandbox.SandboxScenario):
    
    @scenario.configure(context={})
    def create_sandbox(self, sandbox_create_args=None):
        self._create_sandbox(sandbox_create_args)
        
        
    @scenario.configure(context={})    
    def create_and_delete_sandbox(self, sandbox_create_args=None):
        sandboxes = self._create_sandbox(sandbox_create_args)
        self.sleep_between(1, 2) # xxx: add min and max sleep args - l8huang
        self._delete_sandbox(sandboxes)
