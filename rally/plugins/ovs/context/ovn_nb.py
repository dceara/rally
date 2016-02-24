#
# Created on Feb 23, 2016
#
# @author: lhuang8
#

import six
import copy
from rally.common.i18n import _
from rally.common import logging
from rally.common import db
from rally.common import objects
from rally import consts
from rally import exceptions
from rally.task import context
from .. import ovsclients


LOG = logging.getLogger(__name__)


from rally.common.i18n import _
from rally.common import logging
from rally.common import db
from rally.common import objects
from rally import consts
from rally import exceptions
from rally.task import context

@context.configure(name="ovn_nb", order=120)
class OvnNouthbound(context.Context):
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "properties": {
        },
        "additionalProperties": True
    }

    DEFAULT_CONFIG = {
    }

    @logging.log_task_wrapper(LOG.info, _("Enter context: `ovn_nb`"))
    def setup(self):

        controller = self.context["ovn_multihost"]["controller"]
        info = six.next(six.itervalues(controller))
        ovn_nbctl = getattr(ovsclients.Clients(info["credential"]), "ovn-nbctl")()
        ovn_nbctl.set_sandbox("controller-sandbox")
        lswitches = ovn_nbctl.show()

        self.context["ovn-nb"] = lswitches

    @logging.log_task_wrapper(LOG.info, _("Exit context: `ovn_nb`"))
    def cleanup(self):
        pass

