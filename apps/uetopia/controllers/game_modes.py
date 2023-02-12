import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.game_modes import GameModes

class GameModesController(BaseController):
    """Game Modes Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GameModes

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(100)

    def get_by_gameKeyId_onlineSubsystemReference(self, gameKeyId, onlineSubsystemReference):
        """ get single for a gameKey onlineSubsystemReference """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.onlineSubsystemReference == onlineSubsystemReference)
        return query.get()
