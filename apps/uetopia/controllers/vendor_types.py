from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.vendor_types import VendorTypes

class VendorTypesController(BaseController):
    """Vendors Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = VendorTypes

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a gameKey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(100)
