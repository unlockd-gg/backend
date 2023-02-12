import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.game_player_snapshot import GamePlayerSnapshot

class GamePlayerSnapshotController(BaseController):
    """Game Player Snapshot Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GamePlayerSnapshot

    def get_list_by_gamePlayerKeyId(self, gamePlayerKeyId, start_cursor=None, batch_size=5):
        query = self.model.query()
        query = query.filter(self.model.gamePlayerKeyId == gamePlayerKeyId)
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(100, start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def get_list_by_characterKeyId(self, characterKeyId, start_cursor=None, batch_size=5):
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(100, start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more
