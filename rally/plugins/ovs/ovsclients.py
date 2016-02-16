#
# Created on Feb 5, 2016
#
# @author: lhuang8
#

import sys
import abc
import itertools
import collections
import six

from rally.common.plugin import plugin
from rally import exceptions

from utils import get_ssh_from_credential
from utils import py_to_val

_NAMESPACE = "ovs"


def configure(name):
    return plugin.configure(name, namespace=_NAMESPACE)



class OvsClient(plugin.Plugin):
    def __init__(self, credential, cache_obj):
        self.credential = credential
        self.cache = cache_obj
        
    
    @classmethod
    def get(cls, name, namespace=_NAMESPACE):
        return super(OvsClient, cls).get(name, namespace)

    @abc.abstractmethod
    def create_client(self, *args, **kwargs):
        """Create new instance of client."""
        
    def __call__(self, *args, **kwargs):
        """Return initialized client instance."""
        key = "{0}{1}{2}".format(self.get_name(),
                                 str(args) if args else "",
                                 str(kwargs) if kwargs else "")
        if key not in self.cache:
            self.cache[key] = self.create_client(*args, **kwargs)
        return self.cache[key]
        


class Clients(object):
    def __init__(self, credential):
        self.credential = credential
        self.cache = {}
        
    def __getattr__(self, client_name):
        return OvsClient.get(client_name)(self.credential, self.cache)
    
    
    
    def clear(self):
        """Remove all cached client handles."""
        self.cache = {}
    
    
    
    
'''
    def add_br(self, name, may_exist=True, datapath_type=None):
        opts = ['--may-exist'] if may_exist else None
        params = [name]
        if datapath_type:
            params += ['--', 'set', 'Bridge', name,
                       'datapath_type=%s' % datapath_type]
        return BaseCommand(self.context, 'add-br', opts, params)

'''    


@configure("ssh")
class SshClient(OvsClient):


    def create_client(self):
        print "*********   call OvnNbctl.create_client"
        return get_ssh_from_credential(self.credential)
        

@configure("ovn-nbctl")    
class OvnNbctl(OvsClient):
    
    
    class _OvnNbctl(object):
        def __init__(self, credential):
            self.ssh = get_ssh_from_credential(credential)
            self.context = {}
        
        def set_sandbox(self, sandbox):
            self.context["sandbox"] = sandbox    
            
        def run(self, cmd, opts=[], args=[]):
            cmds = []
            sandbox = self.context.get("sandbox")
            if sandbox:
                cmds.append(". %s/sandbox.rc" % sandbox)
            
            
            cmd = itertools.chain(["ovn-nbctl"], opts, [cmd], args)
            cmds.append(" ".join(cmd))
            
            self.ssh.run("\n".join(cmds), 
                         stdout=sys.stdout, stderr=sys.stderr)
            
        def lswitch_add(self, name):
            params = [name]
            
            
            self.run("lswitch-add", args=params)
            
            return {"name":name}
        
        def lswitch_del(self, name):
            params = [name]
            self.run("lswitch-del", args=params)
            
            
        
        def lswitch_list(self):
            self.run("lswitch-list")
            
        
        def show(self, lswitch):
            params = [lswitch] if lswitch else []
            self.run("show", args=params)
        
        def lport_add(self, lswitch, name):
            params =[lswitch, name]
            self.run("lport-add", args=params)
        
            return {"name":name}
        
        
        def lport_list(self, lswitch):
            params =[lswitch]
            self.run("lport-list", args=params)
        
        
        def lport_del(self, name):
            params = [name]
            self.run("lport-del", args=params)
        
        
        def acl_add(self, lswitch, direction, priority, match, action, log=False):
            pass
        
        
        
        
    def create_client(self):
        print "*********   call OvnNbctl.create_client"
        
        client = self._OvnNbctl(self.credential)

        return client



def _set_colval_args(*col_values):
    args = []
    for entry in col_values:
        if len(entry) == 2:
            col, op, val = entry[0], '=', entry[1]
        else:
            col, op, val = entry
        if isinstance(val, collections.Mapping):
            args += ["%s:%s%s%s" % (
                col, k, op, py_to_val(v)) for k, v in val.items()]
        elif (isinstance(val, collections.Sequence)
                and not isinstance(val, six.string_types)):
            if len(val) == 0:
                args.append("%s%s%s" % (col, op, "[]"))
            else:
                args.append(
                    "%s%s%s" % (col, op, ",".join(map(py_to_val, val))))
        else:
            args.append("%s%s%s" % (col, op, py_to_val(val)))
    return args


@configure("ovs-vsctl")    
class OvsVsctl(OvsClient):
    
    class _OvsVsctl(object):
        
        def __init__(self, credential):
            self.ssh = get_ssh_from_credential(credential)
            self.context = {}
            self.batch_mode = False
            self.sandbox = None
            self.cmds = None
            
        def enable_batch_mode(self, value=True):
            self.batch_mode = bool(value) 
            
        def set_sandbox(self, sandbox):
            self.sandbox = sandbox    
 
 
        def run(self, cmd, opts=[], args=[]):
            self.cmds = self.cmds or []
            
            if self.sandbox and self.batch_mode == False:
                self.cmds.append(". %s/sandbox.rc" % self.sandbox)
            
            
            cmd = itertools.chain(["ovs-vsctl"], opts, [cmd], args)
            self.cmds.append(" ".join(cmd))
            
            if self.batch_mode:
                return
            
            self.ssh.run("\n".join(self.cmds), 
                         stdout=sys.stdout, stderr=sys.stderr)
            
            self.cmds = None
            
        def flush(self):
            if self.cmds == None:
                return
            
            if self.sandbox:
                self.cmds.insert(0, ". %s/sandbox.rc" % self.sandbox)
                
            self.ssh.run("\n".join(self.cmds), 
                         stdout=sys.stdout, stderr=sys.stderr)
            
            self.cmds = None
           
 
        def add_port(self, bridge, port, may_exist=True):
            opts = ['--may-exist'] if may_exist else None
            self.run('add-port', opts, [bridge, port])
 
 
        def db_set(self, table, record, *col_values):
            args = [table, record]
            args += _set_colval_args(*col_values)
            self.run("set", args=args)
 
    def create_client(self):
        print "*********   call OvnNbctl.create_client"
        client = self._OvsVsctl(self.credential)
        return client
    



