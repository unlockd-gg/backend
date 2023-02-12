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

class ChatSendHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ChatRoomSendHandler")


        firebaseUser = self.request.get('firebaseUser')


        created = self.request.get('created', datetime.datetime.now().isoformat())
        textMessage = self.request.get('message')

        userKeyId = self.request.get('userKeyId', 'SYSTEM')
        userTitle = self.request.get('userTitle', 'SYSTEM')

        ## push user data to socket server.

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}


        chat_msg = json.dumps({"type":"chat",
                                "textMessage":textMessage,
                                "userKeyId": userKeyId,
                                "userTitle": userTitle,
                                #"chatMessageKeyId": chatMessageKeyId,
                                #"chatChannelTitle": channel.title,
                                #"chatChannelKeyId": channel.key.id(),
                                "created":created
        #"chatChannelRefKey": chatChannelRefKey, "chatChannelRefType": chatChannelRefType
        })

        # push out to in-game clients via heroku
        # ignore if it's failing
        try:
            URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, firebaseUser)
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
