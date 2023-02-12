import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.game_characters import GameCharacters

class GameCharactersController(BaseController):
    """Game Characters Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GameCharacters

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(100)

    def get_online_by_gameKeyId_not_userKeyId(self, gameKeyId, userKeyId):
        """ get possible opponents """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId != userKeyId)
        query = query.filter(self.model.online == True)
        return query.fetch(20)

    def get_list_by_userKeyId(self, userKeyId):
        """ get a truncated list of server user members sorted by modified """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(100)

    def get_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get a gpm by user and game """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_list_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get a gpm by user and game """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)

    def get_online_by_gameKeyId(self, gameKeyId):
        """ get all for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.online == True)
        return query.fetch(100)

    def list_by_gameKeyId(self, gameKeyId, start_cursor=None,):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        entities, cursor, more = query.fetch_page(100,start_cursor=start_cursor)
        return entities, cursor, more

    def list_by_userKeyId(self, userKeyId, start_cursor=None,):
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        entities, cursor, more = query.fetch_page(100,start_cursor=start_cursor)
        return entities, cursor, more

    def list_locked_by_serverKeyId(self, locked_by_serverKeyId, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.locked_by_serverKeyId == locked_by_serverKeyId)
        entities, cursor, more = query.fetch_page(100,start_cursor=start_cursor)
        return entities, cursor, more

    def get_leaderboard_by_lastServerClusterKeyId(self, lastServerClusterKeyId):
        """ get all for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.lastServerClusterKeyId == lastServerClusterKeyId)
        query = query.order(-self.model.rank)
        return query.fetch(20)
