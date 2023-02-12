import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.game_levels import GameLevels

class GameLevelsController(BaseController):
    """Game Levels Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GameLevels


    def list_by_gameKeyId(self, gameKeyId):
        """ get list for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)
