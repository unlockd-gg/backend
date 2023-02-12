import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.game_data import GameData

class GameDataController(BaseController):
    """Game Data Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GameData


    def list_by_gameKeyId(self, gameKeyId):
        """ get list for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def list_page_by_gameKeyId(self, gameKeyId, page_size=20, batch_size=5, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more
