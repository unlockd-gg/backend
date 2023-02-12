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

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GroupGameUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GroupGameUpdateFirebaseHandler")

        ## this is a group_game key
        key_id = self.request.get('key_id')
        groupKeyId = self.request.get('groupKeyId')
        gameKeyId = self.request.get('gameKeyId')



        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        entity = GroupGamesController().get_by_key_id(int(key_id))
        if not entity:
            logging.info('Group Game not found - deleting')
            headers = {"Content-Type": "application/json"}

            URL = "https://ue4topia.firebaseio.com/groups/%s/games/%s.json" % (groupKeyId, gameKeyId)
            resp, content = http_auth.request(URL,
                              "DELETE", ## delete
                              headers=headers)
            return

        ## we have to still push it to firebase so that the group admins can still see it.
        #if not entity.show_game_on_group_page:
        #    logging.info('Group Game not marked to show - deleting')
        #    headers = {"Content-Type": "application/json"}

        #    URL = "https://ue4topia.firebaseio.com/groups/%s/games/%s.json" % (groupKeyId, gameKeyId)
        #    resp, content = http_auth.request(URL,
        #                      "DELETE", ## delete
        #                      headers=headers)
        #    return

        entity_json = json.dumps(entity.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/groups/%s/games/%s.json" % (entity.groupKeyId, entity.gameKeyId)
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          entity_json,
                          headers=headers)

        return
