import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_cluster_players import ServerClusterPlayers

class ServerClusterPlayersController(BaseController):
    """ServerClusterPlayers Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GamePlayers

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(100)

    def get_by_serverClusterKeyId_userKeyId(self, serverClusterKeyId, userKeyId):
        """ get a gpm by user and game """
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()
