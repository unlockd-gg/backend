import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.game_level_links import GameLevelLinks

class GameLevelLinksController(BaseController):
    """Game Level links Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GameLevelLinks


    def list_by_gameLevelKeyId(self, gameLevelKeyId):
        """ get list for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameLevelKeyId == gameLevelKeyId)
        return query.fetch(1000)

    def list_by_gameLevelKeyId_not_return(self, gameLevelKeyId):
        """ get list for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameLevelKeyId == gameLevelKeyId)
        query = query.filter(self.model.isReturnLink == False)
        return query.fetch(1000)

    def get_returnLink_by_gameLevelKeyId(self, gameLevelKeyId):
        """ get list for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameLevelKeyId == gameLevelKeyId)
        query = query.filter(self.model.isReturnLink == True)
        return query.get()
