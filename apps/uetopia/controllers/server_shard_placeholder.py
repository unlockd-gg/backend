import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_shard_placeholder import ServerShardPlaceholder

class ServerShardPlaceholderController(BaseController):
    """ServerShardPlaceholder Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = ServerShardPlaceholder

    def get_serverAssigned_by_serverShardKeyId(self, serverShardKeyId):
        """ get all assigned to a server """

        query = self.model.query()
        query = query.filter(self.model.serverAssigned == True)
        query = query.filter(self.model.serverShardKeyId == serverShardKeyId)
        return query.fetch(1000)

    def get_not_ServerAssigned_by_serverShardTemplateKeyId(self, serverShardTemplateKeyId):
        """ get all NOT ServerAssignedfor a serverShardTemplateKeyId """

        query = self.model.query()
        query = query.filter(self.model.serverAssigned == False)
        query = query.filter(self.model.serverShardTemplateKeyId == serverShardTemplateKeyId)
        return query.fetch(1000)

    def get_by_ServerShardKeyId_UserKeyId(self, serverShardKeyId, userKeyId):
        """ get a single placeholder for a user on a shard """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.serverShardKeyId == serverShardKeyId)
        return query.get()

    def get_by_userKeyId_gameKeyId(self, userKeyId, gameKeyId):
        """ get a single placeholder for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.get()

    def get_stale_by_serverClusterKeyId(self, serverClusterKeyId, staleDateTime):
        """ get a single placeholder for a user """
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.created < staleDateTime)
        return query.fetch(1000)

    def list_by_userKeyId(self,userKeyId):
        """ get a single placeholder for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)
