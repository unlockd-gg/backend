import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.group_games import GroupGames

class GroupGamesController(BaseController):
    """Group Games Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GroupGames

    def get_by_groupKeyId(self, groupKeyId):
        """ get all for a groupKeyId """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        #query = query.order(self.model.created)
        return query.fetch(100)

    def get_by_groupKeyId_gameKeyId(self, groupKeyId, gameKeyId):
        """ get a specific group game connection """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.get()

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a game """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def list_by_gameKeyId(self, gameKeyId, start_cursor=None,):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        entities, cursor, more = query.fetch_page(100,start_cursor=start_cursor)
        return entities, cursor, more
