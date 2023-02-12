import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.group_raids import GroupRaids

class GroupRaidsController(BaseController):
    """Group Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GroupRaids

    def get_by_captainKeyId(self, captainKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.captainKeyId == captainKeyId)
        #query = query.order(self.model.created)
        return query.fetch(100)
