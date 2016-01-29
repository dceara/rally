#
# Created on Jan 29, 2016
#
# @author: lhuang8
#

from consts import ResourceType
from rally.common import sshutils
from rally.common import objects
'''
    Find credential resource from DB by deployment uuid, and return
    info as a dict.
    
    :param deployment deployment uuid
'''
def get_credential_from_resource(deployment):
    
    res = None
    if not isinstance(deployment, objects.Deployment):
        deployment = objects.Deployment.get(deployment)
    
    res = deployment.get_resources(type=ResourceType.CREDENTIAL)

    return res["info"]



def get_ssh_from_credential(cred):
    sshcli = sshutils.SSH(cred["user"], cred["host"], 
                       port = cred["port"], 
                       key_filename = cred["key"],
                       password = cred["password"])
    return sshcli


def get_ssh_client_from_deployment(deployment):
    cred = get_credential_from_resource(deployment)

    return get_ssh_from_credential(cred)

