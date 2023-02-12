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
from apps.uetopia.controllers.groups import GroupsController

from apps.uetopia.controllers.match_results_user import MatchResultsUserController
from apps.uetopia.controllers.event_feed import EventFeedController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GroupEventUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameEventUpdateFirebaseHandler")

        ## this is a group key
        key_id = self.request.get('key_id')

        entity = GroupsController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Group not found')
            return

        eventFeedController = EventFeedController()

        recent_events = eventFeedController.get_recent_by_groupKeyId(entity.key.id())

        if len(recent_events) > 0:
            ## build out the json
            event_array = []
            for recent_event in recent_events:
                event_array.append(recent_event.to_json_for_group())

        entity_json = json.dumps(event_array)

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/groups/%s/eventfeed.json" % entity.key.id()
        logging.info('updating firebase')
        resp, content = http_auth.request(URL,
                          "PUT", ## Put - replace
                          entity_json,
                          headers=headers)

        return
