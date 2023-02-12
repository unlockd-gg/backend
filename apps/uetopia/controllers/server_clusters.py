from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_clusters import ServerClusters

class ServerClustersController(BaseController):
    """ServerCluster Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = ServerClusters

    def list_page_by_userKeyId(self, userKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        items, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return items, cursor, more

    def list_page_by_userKeyId_gameKeyId(self, userKeyId, gameKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        items, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return items, cursor, more

    def list_page_by_gameKeyId(self,  gameKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        items, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return items, cursor, more

    def get_by_gameKeyId(self, gameKeyId):
        """ just get a random one.  TODO get by zone or something else """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.get()

    def get_by_gameKeyId_vm_region(self, gameKeyId, vm_region):
        """ Get a Cluster that matches the region. """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.vm_region == vm_region)
        return query.get()

    def get_by_gameKeyId_vm_region_mmevents(self, gameKeyId, vm_region):
        """ Get a designated Cluster that matches the region. """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.vm_region == vm_region)
        query = query.filter(self.model.accept_matchmaker_events_for_this_region == True)
        return query.get()
