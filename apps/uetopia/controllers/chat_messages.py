import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.chat_messages import ChatMessages

class ChatMessagesController(BaseController):
    """ChatMessages Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = ChatMessages
