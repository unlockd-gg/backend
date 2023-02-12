import logging
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.badges import Badges

class BadgesController(BaseController):
    """Badges Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Badges

    def get_active_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get all for a offerKeyId """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.active == True)
        return query.fetch(1000)

    def get_by_offerKeyId_userKeyId(self, offerKeyId, userKeyId):
        """ get all for a offerKeyId """
        query = self.model.query()
        query = query.filter(self.model.offerKeyId == offerKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_expired(self):
        """ get all expired """
        query = self.model.query()
        query = query.filter(self.model.ends < datetime.datetime.now() )
        return query.fetch(1000)

    def get_active_by_userKeyId(self, userKeyId):
        """ get all for a offerKeyId """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        #query = query.filter(self.model.active == True)  ## Inactive get deleted
        return query.fetch(1000)
