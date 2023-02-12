import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.ads import Ads

class AdsController(BaseController):
    """Ads Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Ads

    def get_not_final_by_gameModeKeyId(self, gameModeKeyId):
        """ get list by game mode key """
        query = self.model.query()
        query = query.filter(self.model.gameModeKeyId == gameModeKeyId)
        query = query.filter(self.model.finalized == False)
        return query.fetch(1000)

    def get_not_final_by_groupKeyId(self, groupKeyId):
        """ get list by developer key """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.finalized == False)
        return query.fetch(1000)

    def get_not_final_by_groupKeyId_gameKeyId(self, groupKeyId, gameKeyId):
        """ get list by group and game """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.finalized == False)
        return query.fetch(1000)

    def get_high_bid_by_gameModeKeyId(self, gameModeKeyId):
        query = self.model.query()
        query = query.filter(self.model.gameModeKeyId == gameModeKeyId)
        query = query.filter(self.model.finalized == False)
        query = query.order(-self.model.bid_per_impression)
        return query.get()

    def get_active_highest_gameModeKeyId(self, gameModeKeyId, quantity):
        """ get list by game mode key """
        query = self.model.query()
        query = query.filter(self.model.gameModeKeyId == gameModeKeyId)
        query = query.filter(self.model.active == True)
        query = query.order(-self.model.bid_per_impression)
        return query.fetch(quantity)
