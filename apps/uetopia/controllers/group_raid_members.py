import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.group_raid_members import GroupRaidMembers

class GroupRaidMembersController(BaseController):
    """Group Raid members Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GroupRaidMembers

    def get_by_userKeyId(self, userKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        #query = query.order(self.model.created)
        return query.fetch(100)

    def get_active_by_userKeyId(self, userKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.raidActive == True)
        return query.get()

    def list_by_groupRaidKeyId(self, groupRaidKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.groupRaidKeyId == groupRaidKeyId)
        return query.fetch(100)
