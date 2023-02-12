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

class ChatChannelDeleteHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ChatChannelDeleteHandler")


        chat_channel_controller = ChatChannelsController()
        chat_channel_subscriber_controller = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        ## incoming we have the chat_channel key_id

        key_id = self.request.get('key_id')
        logging.info('key_id: %s' %key_id)

        ## Find and delete any subscribers first?
        # I don't remember why, but there is a reason why we didn't do this.
        #chat_channel_subscribers = chat_channel_subscriber_controller.get_by_chatChannelKeyId(int(key_id))
        #for chat_channel_subscriber in chat_channel_subscribers:
        #    logging.info('found a chat channel subscriber')
        #    chat_channel_subscriber_controller.delete(chat_channel_subscriber)

        try:
            chat_channel = chat_channel_controller.get_by_key_id(int(key_id))
            logging.info('chat_channel: %s ' %chat_channel.title)
            if not chat_channel:
                logging.error('chat channel not found')
                return
        except:
            logging.error('chat channel not found')
            return






        ## get all of the online subscribers

        chat_channel_subscribers = chat_channel_subscriber_controller.get_by_chatChannelKeyId(int(key_id))

        logging.info("chat_channel_subscribers count: %s"%len(chat_channel_subscribers))


        message="Chat channel: %s closing. /kick" %chat_channel.title

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}
        channel_list_changed_msg = json.dumps({"type":"chat_room_changed_notification",
                                "textMessage": message,
                                #"userKeyId":
        })

        for channel_subscriber in chat_channel_subscribers:
            logging.info('subscriber found')

            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': channel_subscriber.userFirebaseUser,
                                                                                "message": message,
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })

            # push out to in-game clients via heroku
            # ignore if it's failing
            try:
                URL = "%s/user/%s/chat/rooms_changed" % (HEROKU_SOCKETIO_SERVER, channel_subscriber.userFirebaseUser)
                resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  channel_list_changed_msg,
                                  headers=headers)

                logging.info(resp)
                logging.info(content)
            except:
                logging.error('heroku error')

            ## delete the subscriber
            chat_channel_subscriber_controller.delete(channel_subscriber)




        # delete the channel
        chat_channel_controller.delete(chat_channel)



        return
