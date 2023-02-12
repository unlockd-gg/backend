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
from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class TeamUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] TeamUpdateFirebaseHandler")

        ## this is a player's firebase user
        firebaseUser = self.request.get('firebaseUser')


        # push out to in-game clients via heroku
        # ignore if it's failing
        try:
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            team = {'purged': True, 'members': [], 'userIsCaptain': True}

            team_json = json.dumps(team)

            #try:
            URL = "%s/user/%s/team/0" % (HEROKU_SOCKETIO_SERVER, firebaseUser)
            resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  team_json,
                                  headers=headers)

            logging.info(resp)
            logging.info(content)

        except:
            logging.error('heroku error')

        return
