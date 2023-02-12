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

class ChatChannelListChangedHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ChatChannelListChangedHandler")

        firebaseUser = self.request.get('firebaseUser')
        userKeyId = self.request.get('userKeyId')
        textMessage = self.request.get('textMessage')



        ## push user data to socket server.

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        chat_msg = json.dumps({"type":"chat_room_changed_notification",
                                "textMessage": textMessage,
                                "userKeyId": userKeyId
        })

        # push out to in-game clients via heroku
        # ignore if it's failing
        try:
            URL = "%s/user/%s/chat/rooms_changed" % (HEROKU_SOCKETIO_SERVER, firebaseUser)
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
