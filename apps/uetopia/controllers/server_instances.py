from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_instances import ServerInstances

class ServerInstancesController(BaseController):
    """ServerInstances Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = ServerInstances

    def get_any_pending(self):
        """ get any pending record """
        query = self.model.query()
        query = query.filter(self.model.processed == False)
        return query.get()

    def get_by_serverKeyId(self, serverKeyId):
        """ get a server list by server key """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        return query.fetch(1000)

    def get_by_gameKeyId(self, gameKeyId):
        """ get a server list by game key """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def get_pending_by_gameKeyId(self, gameKeyId):
        """ get a server list by game key """
        query = self.model.query()
        query = query.filter(self.model.processed == False)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def get_pending_by_serverKeyId(self, serverKeyId):
        """ get a server list by server key """
        query = self.model.query()
        query = query.filter(self.model.processed == False)
        query = query.filter(self.model.serverKeyId == serverKeyId)
        return query.fetch(1000)
