import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.chat_channel_subscribers import ChatChannelSubscribers

class ChatChannelSubscribersController(BaseController):
    """ChatChannelSubscribers Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = ChatChannelSubscribers

    def get_by_chatChannelKeyId(self, chatChannelKeyId):
        """ get all subscribers for a chatChannel """
        query = self.model.query()
        query = query.filter(self.model.chatChannelKeyId == chatChannelKeyId)
        #query = query.filter(self.model.online == True)
        #query = query.order(-self.model.created)
        return query.fetch(200)

    def get_by_channel_and_user(self, chatChannelKeyId, userKeyId):
        """ get a channel subscrtiber """
        query = self.model.query()
        query = query.filter(self.model.chatChannelKeyId == chatChannelKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_by_user(self, userKeyId):
        """ get a channel subscrtiber """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(20)
