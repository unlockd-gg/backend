import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.chat_channels import ChatChannels

class ChatChannelsController(BaseController):
    """ChatChannels Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = ChatChannels

    def get_by_channel_type_refKeyId(self, channel_type, refKeyId):
        """ get a chat channel """
        query = self.model.query()
        query = query.filter(self.model.channel_type == channel_type)
        query = query.filter(self.model.refKeyId == refKeyId)
        return query.get()

    def get_custom_by_title(self, title):
        """ get a chat channel """
        query = self.model.query()
        query = query.filter(self.model.channel_type == "custom")
        query = query.filter(self.model.title == title)
        return query.get()

    def get_by_title(self, title):
        """ get a chat channel """
        query = self.model.query()
        query = query.filter(self.model.title == title)
        return query.get()

    def get_all_by_adminUserKeyId(self, adminUserKeyId):
        """ get a chat channel """
        query = self.model.query()
        query = query.filter(self.model.adminUserKeyId == adminUserKeyId)
        return query.fetch(200)
