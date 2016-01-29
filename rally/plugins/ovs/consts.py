#
# Created on Jan 29, 2016
#
# @author: lhuang8
#


from rally.common import utils


class _ResourceType(utils.ImmutableMixin, utils.EnumMixin):
    CREDENTIAL = "credentials"
    
ResourceType = _ResourceType()


