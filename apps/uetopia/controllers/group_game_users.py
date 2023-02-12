import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.group_game_users import GroupGameUsers

class GroupGameUsersController(BaseController):
    """Group Game Users Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GroupGameUsers

    def get_by_groupKeyId(self, groupKeyId):
        """ get all for a slugifyUrl """

        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        #query = query.order(self.model.created)
        return query.fetch(100)

    def get_by_groupKeyId_userKeyId_gameKeyId(self, groupKeyId, userKeyId, gameKeyId):
        """ get a gpm by player and group """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.get()

    def get_list_by_userKeyId(self, userKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(100)
