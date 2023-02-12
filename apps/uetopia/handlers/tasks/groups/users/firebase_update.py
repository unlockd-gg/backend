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

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GroupUserUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GroupUserUpdateFirebaseHandler")

        ## this is a game_player key
        key_id = self.request.get('key_id')

        entity = GroupUsersController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Group User not found')
            return

        """
        ## get the group role and attach permissions to the group user
        group_user_role = GroupRolesController().get_by_key_id(entity.roleKeyId)
        if not group_user_role:
            logging.error('Group User Role not found')
            return

        entity.update_group_settings = group_user_role.update_group_settings
        entity.update_group_roles = group_user_role.update_group_roles
        entity.update_player_roles = group_user_role.update_player_roles
        entity.create_events = group_user_role.create_events
        entity.update_events = group_user_role.update_events
        entity.update_games = group_user_role.update_games
        entity.update_servers = group_user_role.update_servers
        entity.create_matches = group_user_role.create_matches
        entity.create_tournaments = group_user_role.create_tournaments
        """

        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        #entity_json = json.dumps(entity.to_json_with_roles())
        entity_json = json.dumps(entity.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/groups/%s/users/%s.json" % (entity.groupKeyId, entity.firebaseUser)
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          entity_json,
                          headers=headers)

        return
