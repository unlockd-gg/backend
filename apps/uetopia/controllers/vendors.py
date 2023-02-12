import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.vendors import Vendors

class VendorsController(BaseController):
    """Vendors Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Vendors

    def get_by_serverKeyId(self, serverKeyId):
        """ get all for a serverKey """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        return query.fetch(1000)

    def get_expired(self):
        """ get all expired """
        query = self.model.query()
        past_date = datetime.datetime.now() - datetime.timedelta(days=60)
        query = query.filter(self.model.modified < past_date )
        return query.fetch(1)
