#
# Created on Jan 16, 2016
#
# @author: lhuang8
#


""" Rally OVS command: deployment """
from __future__ import print_function

import json
import os
import re
import sys

import jsonschema
from six.moves.urllib import parse
import yaml


from rally import api
from rally.cli import cliutils
from rally.cli import envutils
from rally.common import fileutils
from rally.common.i18n import _
from rally.common import utils
from rally import exceptions
from rally import plugins

      
class DeploymentCommands(object):
    """Set of commands that allow you to manage ovs deployments."""
    
    
    @cliutils.args("--name", type=str, required=True,
               help="A name of the ovs deployment.")
    @cliutils.args("--filename", type=str, required=True, metavar="<path>",
               help="A path to the configuration file of the ovs deployment.")
    @plugins.ensure_plugins_are_loaded
    def create(self, name, filename):
        """Create new deployment."""
        
        filename = os.path.expanduser(filename)
        print("file:" + filename)
        
        with open(filename, "rb") as deploy_file:
            config = yaml.safe_load(deploy_file.read())
        
        dict(config)    
        
        try:
            deployment = api.Deployment.create(config, name)
        except jsonschema.ValidationError:
            print(_("Config schema validation error: %s.") % sys.exc_info()[1])
            return(1)
        except exceptions.DeploymentNameExists:
            print(_("Error: %s") % sys.exc_info()[1])
            return(1)
        
        
        





