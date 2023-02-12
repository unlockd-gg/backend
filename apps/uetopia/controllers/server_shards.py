from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_shards import ServerShards

class ServerShardsController(BaseController):
    """ServerShards Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = ServerShards

    def get_by_serverShardKeyId(self, serverShardKeyId):
        """ get a server shard by the server key """
        query = self.model.query()
        query = query.filter(self.model.serverShardKeyId == serverShardKeyId)
        return query.get()

    def get_list_by_serverShardTemplateKeyId(self, serverShardTemplateKeyId):
        """ get a server shard by the server key """
        query = self.model.query()
        query = query.filter(self.model.serverShardTemplateKeyId == serverShardTemplateKeyId)
        return query.fetch(1000)


    def get_by_gameKeyId(self, gameKeyId):
        """ get all server shards by the game key """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)
