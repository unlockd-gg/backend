import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.group_users import GroupUsers

class GroupUsersController(BaseController):
    """Group Users Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GroupUsers

    def get_by_groupKeyId(self, groupKeyId):
        """ get all for a slugifyUrl """

        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        #query = query.order(self.model.created)
        return query.fetch(100)

    def get_list_truncated_by_group(self, groupKeyId, modifiedDate, limit):
        """ get a truncated list of server player members sorted by modified """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.modified >= modifiedDate)
        query = query.order(-self.model.modified)
        return query.fetch(limit)

    def get_by_groupKeyId_userKeyId(self, groupKeyId, userKeyId):
        """ get a gpm by player and group """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_list_by_userKeyId(self, userKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(100)
