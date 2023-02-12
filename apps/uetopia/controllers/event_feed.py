import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.event_feed import EventFeed

class EventFeedController(BaseController):
    """EventFeed Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = EventFeed


    def get_recent_by_gameKeyId(self, gameKeyId):
        """ get recent events for a game """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.order(-self.model.created)
        return query.fetch(10)

    def get_recent_by_serverClusterKeyId(self, serverClusterKeyId):
        """ get recent events for a game """
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.order(-self.model.created)
        return query.fetch(10)
        
    def get_recent_by_groupKeyId(self, groupKeyId):
        """ get recent events for a game """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.order(-self.model.created)
        return query.fetch(10)

    def get_recent_by_userKeyId(self, userKeyId):
        """ get recent events for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.order(-self.model.created)
        return query.fetch(10)
