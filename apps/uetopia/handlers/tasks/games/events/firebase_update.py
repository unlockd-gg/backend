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

from apps.uetopia.controllers.match_results_user import MatchResultsUserController
from apps.uetopia.controllers.event_feed import EventFeedController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GameEventUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameEventUpdateFirebaseHandler")

        ## this is a game key
        key_id = self.request.get('key_id')

        entity = GamesController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Game not found')
            return

        ## push user data to firebase.  overwrite.
        # for matchmaker games we want the list of matches
        # for persistent games we want the list of matchresultuser events

        eventFeedController = EventFeedController()

        recent_events = eventFeedController.get_recent_by_gameKeyId(entity.key.id())

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

        URL = "https://ue4topia.firebaseio.com/games/%s/eventfeed.json" % entity.key.id()
        #if entity.invisible:
        #    logging.info('deleting the invisible game from firebase')
        #    resp, content = http_auth.request(URL,
        #                  "DELETE", ## We can delete data with a DELETE request
        #                  entity_json,
        #                  headers=headers)
        #else:
        logging.info('updating firebase')
        resp, content = http_auth.request(URL,
                          "PUT", ## Put - replace
                          entity_json,
                          headers=headers)

        return
