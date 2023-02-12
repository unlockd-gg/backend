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
from apps.uetopia.controllers.user_relationships import UserRelationshipsController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class FriendUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] FriendUpdateFirebaseHandler")

        ## this is a userKeyId
        key_id = self.request.get('key_id')
        user = UsersController().get_by_key_id(int(key_id))
        if not user:
            logging.error('User not found')
            return

        ## optional varables for current play
        playingGame = self.request.get('playingGame', None)
        playingGameKeyId = self.request.get('playingGameKeyId', None)
        playingOnServer = self.request.get('playingOnServer', None)
        playingOnServerKeyId = self.request.get('playingOnServerKeyId', None)
        playingLink = self.request.get('playingLink', None)
        online = self.request.get('online', 'False')
        streaming = self.request.get('streaming', 'False')
        streamLink = self.request.get('streamLink', None)

        ## convert online to bool
        if online == "False":
            online = False
        else:
            online = True

        if streaming == "False":
            streaming = False
        else:
            streaming = True

        ## get rid of nones
        if playingGame == "None":
            playingGame = None

        if playingGameKeyId == "None":
            playingGameKeyId = None

        if playingOnServer == "None":
            playingOnServer = None

        if playingOnServerKeyId == "None":
            playingOnServerKeyId = None

        if playingLink == "None":
            playingLink = None

        urController = UserRelationshipsController()


        relationships = urController.get_list_confirmed_by_userTargetKeyId(int(key_id))
        if not relationships:
            logging.info('relationships not found') # this is ok.  Some people don't have friends.
            return

        ## use group tag if set
        if user.groupTag:
            player_name = user.groupTag + " " + user.title
        else:
            player_name = user.title

        ## push user data to firebase.  overwrite.

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        for relationship in relationships:
            relationship.playingGame = playingGame
            if playingGameKeyId:
                relationship.playingGameKeyId = int(playingGameKeyId)
            relationship.playingOnServer = playingOnServer
            if playingOnServerKeyId:
                relationship.playingOnServerKeyId = int(playingOnServerKeyId)
            relationship.playingLink = playingLink
            relationship.online = online
            relationship.userTargetTitle = player_name
            ## update user relationship
            urController.update(relationship)

            ## user relationships don't store streaming state right now.
            relationship.streaming = streaming
            relationship.streamLink = streamLink
            relationship_json = json.dumps(relationship.to_json_with_status())
            headers = {"Content-Type": "application/json"}

            URL = "https://ue4topia.firebaseio.com/users/%s/friends/%s.json" % (relationship.userFirebaseUser, relationship.userTargetKeyId)
            resp, content = http_auth.request(URL,
                                ##"PATCH",
                              "PUT", ## Write or replace data to a defined path,
                              relationship_json,
                              headers=headers)

            logging.info(resp)
            logging.info(content)

            # push out to in-game clients via heroku
            # ignore if it's failing
            try:
                URL = "%s/user/%s/friend/%s" % (HEROKU_SOCKETIO_SERVER, relationship.userFirebaseUser, relationship.userTargetKeyId)
                resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  relationship_json,
                                  headers=headers)

                logging.info(resp)
                logging.info(content)
            except:
                logging.error('heroku error')

        return
