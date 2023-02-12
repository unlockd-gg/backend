import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.offers import Offers

class OffersController(BaseController):
    """Offers Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Offers

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a game """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def get_visible_active_by_gameKeyId(self, gameKeyId):
        """ get all for a game """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.visible == True)
        query = query.filter(self.model.active == True)
        return query.fetch(1000)
