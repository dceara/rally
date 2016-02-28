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
import pipes

from rally.common.plugin import plugin
from rally import exceptions

from utils import get_ssh_from_credential
from utils import py_to_val
from StringIO import StringIO

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




'''
    lswitch 48732e5d-b018-4bad-a1b6-8dbc762f4126 (lswitch_c52f4c_xFG42O)
        lport lport_c52f4c_LXzXCE
        lport lport_c52f4c_dkZSDg
    lswitch 7f55c582-c007-4fba-810d-a14ead480851 (lswitch_c52f4c_Rv0Jcj)
        lport lport_c52f4c_cm8SIf
        lport lport_c52f4c_8h7hn2
    lswitch 9fea76cf-d73e-4dc8-a2a3-1e98b9d8eab0 (lswitch_c52f4c_T0m6Ce)
        lport lport_c52f4c_X3px3u
        lport lport_c52f4c_92dhqb

'''

def get_lswitch_info(info):
    '''
    @param info output of 'ovn-nbctl show'
    '''

    lswitches = []

    lswitch = None
    for line in info.splitlines():
        tokens = line.strip().split(" ")
        if tokens[0] == "lswitch":
            name = tokens[2][1:-1]
            lswitch = {"name":name, "uuid":tokens[1], "lports":[]}
            lswitches.append(lswitch)
        elif tokens[0] == "lport":
            name = tokens[1][1:-1]
            lswitch["lports"].append({"name":name})

    return lswitches


class DdCtlMixin(object):

    def get(self, table, record, *col_values):
        args = [table, record]
        args += _set_colval_args(*col_values)
        self.run("get", args=args)


    def list(self, table, records):
        args = [table]
        args += records
        self.run("list", args=args)

    def wait_until(self, table, record, *col_values):
        args = [table, record]
        args += _set_colval_args(*col_values)
        self.run("wait-until", args=args)


@configure("ovn-nbctl")
class OvnNbctl(OvsClient):


    class _OvnNbctl(DdCtlMixin):
        def __init__(self, credential):
            self.ssh = get_ssh_from_credential(credential)
            self.context = {}
            self.sandbox = None
            self.batch_mode = False
            self.cmds = None

        def enable_batch_mode(self, value=True):
            self.batch_mode = bool(value)

        def set_sandbox(self, sandbox):
            self.sandbox = sandbox

        def run(self, cmd, opts=[], args=[], stdout=sys.stdout, stderr=sys.stderr):
            self.cmds = self.cmds or []

            if self.batch_mode:
                cmd = itertools.chain([" -- "], opts, [cmd], args)
                self.cmds.append(" ".join(cmd))
                return

            if self.sandbox:
                self.cmds.append(". %s/sandbox.rc" % self.sandbox)

            cmd = itertools.chain(["ovn-nbctl"], opts, [cmd], args)
            self.cmds.append(" ".join(cmd))

            self.ssh.run("\n".join(self.cmds),
                         stdout=stdout, stderr=stderr)

            self.cmds = None


        def flush(self):
            if self.cmds == None or len(self.cmds) == 0:
                return

            run_cmds = []
            if self.sandbox:
                run_cmds.append(". %s/sandbox.rc" % self.sandbox)

            run_cmds.append("ovn-nbctl" + " ".join(self.cmds))
            self.ssh.run("\n".join(run_cmds),
                         stdout=sys.stdout, stderr=sys.stderr)

            self.cmds = None


        def lswitch_add(self, name):
            params = [name]


            self.run("lswitch-add", args=params)

            return {"name":name}

        def lswitch_del(self, name):
            params = [name]
            self.run("lswitch-del", args=params)



        def lswitch_list(self):
            self.run("lswitch-list")

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


        def acl_add(self, lswitch, direction, priority, match, action,
                    log=False):
            opts = ["--log"] if log else []
            match = pipes.quote(match)
            params = [lswitch, direction, str(priority), match, action]
            self.run("acl-add", opts, params)

        def acl_list(self, lswitch):
            params = [lswitch]
            self.run("acl-list", args=params)


        def acl_del(self, lswitch):
            params = [lswitch]
            self.run("acl-del", args=params)

        def show(self, lswitch=None):
            params = [lswitch] if lswitch else []
            stdout = StringIO()
            self.run("show", args=params, stdout=stdout)
            output = stdout.getvalue()

            return get_lswitch_info(output)

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




