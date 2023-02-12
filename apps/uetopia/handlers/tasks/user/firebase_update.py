import endpoints
import logging
import uuid
import urllib
import json
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

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class UserUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] UserUpdateFirebaseHandler")


        key_id = self.request.get('key_id')

        user = UsersController().get_by_key_id(int(key_id))
        if not user:
            logging.error('User not found')
            return

        ## ALL PRESENCE MOVED TO HANDLERS/WEBHOOKS/
        """
        ## optional varables for current play
        playingGame = self.request.get('playingGame', None)
        playingGameKeyId = self.request.get('playingGameKeyId', None)
        playingOnServer = self.request.get('playingOnServer', None)
        playingOnServerKeyId = self.request.get('playingOnServerKeyId', None)
        playingLink = self.request.get('playingLink', None)
        online = self.request.get('online', 'False')
        streaming = self.request.get('streaming', 'False')
        skip_friends = self.request.get('skip_friends', 'False')
        skip_presence = self.request.get('skip_presence', 'False')

        ## convert online to bool
        if online == "False":
            online = False
        else:
            online = True

        if streaming == "False":
            streaming = False
        else:
            streaming = True

        if skip_friends == "False":
            skip_friends = False
        else:
            skip_friends = True

        if skip_presence == "False":
            skip_presence = False
        else:
            skip_presence = True



        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())

        if user.online:
            logging.info('user is online')
            if user.twitch_streamer:
                logging.info('twitch streamer found - checking stream status')
                headers = {"Content-Type": "application/json", "Client-ID": TWITCH_CLIENT_ID}
                URL = "https://api.twitch.tv/helix/streams?user_id=%s" % user.twitch_channel_id

                try:
                    resp, content = http_auth.request(URL,
                                        "GET",
                                      ##"PUT", ## Write or replace data to a defined path,
                                      #user_json,
                                      headers=headers)

                    logging.info(resp)
                    logging.info(content)
                    stream_info_json = json.loads(content)
                    if stream_info_json['stream']:
                        logging.info('stream info found')
                        user.twitch_currently_streaming = True
                        user.twitch_stream_game = stream_info_json['stream']['game']
                        user.twitch_stream_viewers = stream_info_json['stream']['viewers']
                    else:
                        user.twitch_currently_streaming = False
                except:
                    user.twitch_currently_streaming = False
                    user.twitch_stream_game = ""
                    user.twitch_stream_viewers = 0
        else:
            logging.info('user is offline')
            user.twitch_currently_streaming = False
            user.twitch_stream_game = ""
            user.twitch_stream_viewers = 0


        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        if not skip_friends:
            ## set all of the user relationships
            taskUrl='/task/user/friends/firebase/update'
            if user.twitch_streamer:
                streamLink='https://www.twitch.tv/%s'%user.twitch_channel_id
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                                    'online': user.online,
                                                                                    'streaming': user.twitch_currently_streaming,
                                                                                    'streamLink':streamLink,
                                                                                    'playingGame': playingGame,
                                                                                    'playingGameKeyId': playingGameKeyId,
                                                                                    'playingOnServer': playingOnServer,
                                                                                    'playingOnServerKeyId': playingOnServerKeyId,
                                                                                    'playingLink': playingLink}, countdown = 2,)

            else:
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                                'online': user.online,
                                                                                'playingGame': playingGame,
                                                                                'playingGameKeyId': playingGameKeyId,
                                                                                'playingOnServer': playingOnServer,
                                                                                'playingOnServerKeyId': playingOnServerKeyId,
                                                                                'playingLink': playingLink}, countdown = 2,)



        """
        user_json = json.dumps(user.to_json())

        #logging.info(model_json)
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())

        headers = {"Content-Type": "application/json"}
        URL = "https://ue4topia.firebaseio.com/users/%s.json" % user.firebaseUser
        resp, content = http_auth.request(URL,
                            "PATCH",
                          ##"PUT", ## Write or replace data to a defined path,
                          user_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        user_json_pub = json.dumps(user.to_json_public())

        URL = "https://ue4topia.firebaseio.com/users-public/%s.json" % user.key.id()
        resp, content = http_auth.request(URL,
                            "PATCH",
                          ##"PUT", ## Write or replace data to a defined path,
                          user_json_pub,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        ## Muting this.  It just does not work.
        #if not skip_presence:
        #    logging.info('updating presence')
        #    logging.info(user_json_pub)
        #    URL = "https://ue4topia.firebaseio.com/presence/%s.json" % user.firebaseUser
        #    resp, content = http_auth.request(URL,
        #                        "PATCH",
        #                      ##"PUT", ## Write or replace data to a defined path,
        #                      user_json_pub,
        #                      headers=headers)

        #    logging.info(resp)
        #    logging.info(content)



        return
