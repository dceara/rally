#
# Created on Jan 29, 2016
#
# @author: lhuang8
#

import random

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



def get_random_sandbox(sandboxes):
    info = random.choice(sandboxes)
    sandbox = random.choice(info["sandboxes"])

    return info["farm"], sandbox



def get_random_mac(base_mac):
    mac = [int(base_mac[0], 16), int(base_mac[1], 16),
           int(base_mac[2], 16), random.randint(0x00, 0xff),
           random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    if base_mac[3] != '00':
        mac[3] = int(base_mac[3], 16)
    return ':'.join(["%02x" % x for x in mac])


def py_to_val(pyval):
    """Convert python value to ovs-vsctl value argument"""
    if isinstance(pyval, bool):
        return 'true' if pyval is True else 'false'
    elif pyval == '':
        return '""'
    else:
        return pyval

