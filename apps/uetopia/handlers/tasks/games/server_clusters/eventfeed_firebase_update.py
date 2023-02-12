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

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController

from apps.uetopia.controllers.match_results_user import MatchResultsUserController
from apps.uetopia.controllers.event_feed import EventFeedController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ClusterEventUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ClusterEventUpdateFirebaseHandler")

        ## this is a server cluster key
        key_id = self.request.get('key_id')

        entity = ServerClustersController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Cluster not found')
            return

        ## push user data to firebase.  overwrite.
        # for matchmaker games we want the list of matches
        # for persistent games we want the list of matchresultuser events

        eventFeedController = EventFeedController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameCharacterController = GameCharactersController()

        recent_events = eventFeedController.get_recent_by_serverClusterKeyId(entity.key.id())

        if len(recent_events) > 0:
            ## build out the json
            event_array = []
            for recent_event in recent_events:
                event_array.append(recent_event.to_json_for_game())

        entity_json = json.dumps(event_array)

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/games/%s/clusters/%s/eventfeed.json" % (entity.gameKeyId, entity.key.id() )

        logging.info('updating firebase')
        resp, content = http_auth.request(URL,
                          "PUT", ## Put - replace
                          entity_json,
                          headers=headers)

        ## Do the leaderboard here too.
        ## first check to see if the game uses characters
        game = gameController.get_by_key_id(entity.gameKeyId)

        if not game:
            logging.info('did not find game')
            return

        leaderboard_array = []

        if game.characters_enabled:
            logging.info('game uses characters')

            leaderboard_characters = gameCharacterController.get_leaderboard_by_lastServerClusterKeyId(entity.key.id() )

            for leaderboard_character in leaderboard_characters:
                logging.info('found leaderboard character')
                leaderboard_array.append(leaderboard_character.to_json_public() )

        else:
            logging.info('game does not use characters')

            leaderboard_characters = gamePlayerController.get_leaderboard_by_lastServerClusterKeyId(entity.key.id() )

            for leaderboard_character in leaderboard_characters:
                logging.info('found leaderboard character')
                leaderboard_array.append(leaderboard_character.to_json_public() )

        leaderboard_json = json.dumps(leaderboard_array)

        URL = "https://ue4topia.firebaseio.com/games/%s/clusters/%s/leaderboard.json" % (entity.gameKeyId, entity.key.id() )

        logging.info('updating firebase leaderboard')
        resp, content = http_auth.request(URL,
                          "PUT", ## Put - replace
                          leaderboard_json,
                          headers=headers)



        return
