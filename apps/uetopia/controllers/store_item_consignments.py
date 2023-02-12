from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.store_item_consignments import StoreItemConsignments

class StoreItemConsignmentsController(BaseController):
    """StoreItemConsignments Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = StoreItemConsignments

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a gameKeyId """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)
