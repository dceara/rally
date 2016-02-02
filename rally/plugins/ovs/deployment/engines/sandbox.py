
#
# Created on Jan 16, 2016
#
# @author: lhuang8
#


import os
import sys
import six
from six.moves.urllib import parse
import subprocess


from rally.common.i18n import _
from rally.common import logging
from rally.common import objects
from rally import consts
from rally.deployment import engine # XXX: need a ovs one?
from rally.deployment.serverprovider import provider

from . import get_script
from . import get_script_path
from . import get_updated_server
from . import OVS_USER
from . import OVS_REPO
from . import OVS_BRANCH



class SandboxEngine(engine.Engine):
    """ base engine
    """
    
    
    def __init__(self, deployment):
        super(SandboxEngine, self).__init__(deployment)


    '''
        create user in host if necessary
        
        :param user A user name used to run test, give it sudo premission with 
                    no password. 
    '''
    def _prepare(self, server, user):
        server.ssh.run("/bin/bash -e -s %s" % user, stdin=get_script("prepare.sh"),
                            stdout=sys.stdout, stderr=sys.stderr);

        if server.password:
            server.ssh.run("chpasswd",
                           stdin="%s:%s" % (user, server.password))


    def _put_file(self, server, filename):
        localpath = get_script_path(filename)
        server.ssh.put_file(localpath, filename)
        


    '''
        install ovs from source code as 
    '''
    def _install_ovs(self, server):
        ovs_repo = self.config.get("ovs_repo", OVS_REPO)
        ovs_branch = self.config.get("ovs_branch", OVS_BRANCH)
        ovs_user = self.config.get("ovs_user", OVS_USER)

        http_proxy = self.config.get("http_proxy", None)
        https_proxy = self.config.get("https_proxy", None)
        
        ovs_server = get_updated_server(server, user=ovs_user)
        self._put_file(ovs_server, "install.sh")
        self._put_file(ovs_server, "ovs-sandbox.sh")
        
        
        cmds = []
        if http_proxy or https_proxy :
            cmd = '''cat > proxy_env.sh <<EOF
export http_proxy=$http_proxy 
export https_proxy=$https_proxy
EOF
'''
            cmds.append(cmd)
            cmds.append("echo 'use http proxy in proxy_env.sh")
            cmds.append(". proxy_env.sh;")
        
        
        cmd = "./install.sh %s %s %s" % (ovs_repo, ovs_branch, ovs_user)
        cmds.append(cmd)
        
        ovs_server.ssh.run(";".join(cmds),
                            stdout=sys.stdout, stderr=sys.stderr);

 


    def _deploy(self, server):
        
        ovs_user = self.config.get("ovs_user", OVS_USER)
        self._prepare(server, ovs_user)
        
        self._install_ovs(server)
        
        
        






