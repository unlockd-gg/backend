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

#from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GamePlayerUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GamePlayerUpdateFirebaseHandler")

        ## this is a game_player key
        key_id = self.request.get('key_id')

        entity = GamePlayersController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Game Player not found')
            return

        ## check to see if characters are enabled, if so...  go though the characters and do some math
        gameCharacterController = GameCharactersController()
        if entity.characterCurrentKeyId:
            logging.info('found character id')
            all_player_characters = gameCharacterController.get_list_by_gameKeyId_userKeyId(entity.gameKeyId, entity.userKeyId)

            score_sum = 0
            score = 0
            rank = 0

            for player_character in all_player_characters:
                logging.info('found character')
                if player_character.rank > rank:
                    rank = player_character.rank
                if player_character.score:
                    score_sum = score_sum + player_character.score

            if score_sum:
                score = score_sum / len(all_player_characters)

            entity.score = score
            entity.rank = rank

        ## push user data to firebase.  overwrite.

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        entity_json = json.dumps(entity.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/games/%s/players/%s.json" % (entity.gameKeyId, entity.firebaseUser)
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          entity_json,
                          headers=headers)

        entity_json = json.dumps(entity.to_json_public())

        if entity.showGameOnProfile:

            URL = "https://ue4topia.firebaseio.com/users-public/%s/games/%s.json" % (entity.userKeyId, entity.key.id())
            resp, content = http_auth.request(URL,
                              "PUT", ## Write or replace data to a defined path,
                              entity_json,
                              headers=headers)
        else:
            URL = "https://ue4topia.firebaseio.com/users-public/%s/games/%s.json" % (entity.userKeyId, entity.key.id())
            resp, content = http_auth.request(URL,
                              "DELETE", ## Remove it
                              entity_json,
                              headers=headers)

        return
