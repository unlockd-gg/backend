import endpoints
import logging
import uuid
import urllib
import json
import datetime
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

##from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ChatChannelSendHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ChatChannelSendHandler")

        ## this is a Chat Channel Key ID
        key_id = self.request.get('key_id')
        ## get the team
        channel = ChatChannelsController().get_by_key_id(int(key_id))

        if not channel:
            logging.error('channel not found')
            return



        chatChannelSubscribersController = ChatChannelSubscribersController()


        chat_subscribers = chatChannelSubscribersController.get_by_chatChannelKeyId(int(key_id))
        if not chat_subscribers:
            logging.info('chat_subscribers not found')
            return

        now = datetime.datetime.now()
        created = self.request.get('created', now.isoformat())
        textMessage = self.request.get('message')
        chatMessageKeyId = self.request.get('chatMessageKeyId')
        userKeyId = self.request.get('userKeyId', 'SYSTEM')
        userTitle = self.request.get('userTitle', 'SYSTEM')
        chatChannelTitle = self.request.get('chatChannelTitle')
        #chatChannelData = self.request.get('chatChannelData', None)
        chatChannelRefKey = self.request.get('chatChannelRefKey', None)
        chatChannelRefType = self.request.get('chatChannelRefType', None)

        ## push user data to socket server.

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}


        for chat_subscriber in chat_subscribers:

            chat_msg = json.dumps({"type":"chat",
                                    "textMessage":textMessage,
                                    "userKeyId": userKeyId,
                                    "userTitle": userTitle,
                                    "chatMessageKeyId": chatMessageKeyId,
                                    "chatChannelTitle": channel.title,
                                    "chatChannelKeyId": channel.key.id(),
                                    "created":created
            #"chatChannelRefKey": chatChannelRefKey, "chatChannelRefType": chatChannelRefType
            })

            # push out to in-game clients via heroku
            # ignore if it's failing
            try:
                URL = "%s/user/%s/roomchat/%s" % (HEROKU_SOCKETIO_SERVER, chat_subscriber.userFirebaseUser, chatMessageKeyId)
                resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  chat_msg,
                                  headers=headers)

                logging.info(resp)
                logging.info(content)
            except:
                logging.error('heroku error')

        return
