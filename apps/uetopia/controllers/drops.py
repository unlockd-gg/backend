import logging
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.drops import Drops

class DropsController(BaseController):
    """Drops Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Drops

    def get_by_gamePlayerKeyId(self, gamePlayerKeyId):
        """ get all for a offerKeyId """
        query = self.model.query()
        query = query.filter(self.model.gamePlayerKeyId == gamePlayerKeyId)
        return query.fetch(1000)
