from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_links import ServerLinks

class ServerLinksController(BaseController):
    """ServerLinks Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = ServerLinks

    def list_page_by_userKeyId_originServerKeyId(self, userKeyId, originServerKeyId, page_size=20, batch_size=5, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.originServerKeyId == originServerKeyId)
        items, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return items, cursor, more

    def get_by_originServerKeyId_targetServerKeyId(self, originServerKeyId, targetServerKeyId):
        query = self.model.query()
        query = query.filter(self.model.originServerKeyId == originServerKeyId)
        query = query.filter(self.model.targetServerKeyId == targetServerKeyId)
        return query.get()

    def get_list_by_originServerKeyId(self, originServerKeyId):
        query = self.model.query()
        query = query.filter(self.model.originServerKeyId == originServerKeyId)
        return query.fetch(1000)

    def get_list_by_targetServerKeyId(self, targetServerKeyId):
        query = self.model.query()
        query = query.filter(self.model.targetServerKeyId == targetServerKeyId)
        return query.fetch(1000)

    def get_by_gameKeyId(self, gameKeyId):
        """ get all links by the game key """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)
