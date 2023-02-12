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
from apps.uetopia.controllers.offers import OffersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GameUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameUpdateFirebaseHandler")

        ## this is a game key
        key_id = self.request.get('key_id')

        entity = GamesController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Game not found')
            return

        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        game_modes = GameModesController().get_by_gameKeyId(entity.key.id())

        game_modes_json = []

        for gmode in game_modes:
            game_modes_json.append(gmode.to_json())

        entity.game_modes = game_modes_json

        offers = OffersController().get_visible_active_by_gameKeyId(entity.key.id())

        offers_json = []
        for offer in offers:
            offers_json.append(offer.to_json())

        entity.offers = offers_json

        entity_json = json.dumps(entity.to_json_with_modes_offers())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/games/%s.json" % entity.key.id()
        #if entity.invisible:
        #    logging.info('deleting the invisible game from firebase')
        #    resp, content = http_auth.request(URL,
        #                  "DELETE", ## We can delete data with a DELETE request
        #                  entity_json,
        #                  headers=headers)
        #else:
        logging.info('updating firebase')
        resp, content = http_auth.request(URL,
                          "PATCH", ## We can update specific children at a location without overwriting existing data using a PATCH request.
                          ## Named children in the data being written with PATCH will be overwritten, but omitted children will not be deleted.
                          entity_json,
                          headers=headers)

        return
