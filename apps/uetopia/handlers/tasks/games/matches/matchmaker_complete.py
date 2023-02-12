import endpoints
import logging
import uuid
import urllib
import json
import copy
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from protorpc import remote
from google.appengine.api import taskqueue

from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.handlers import BaseHandler

from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController


from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class MatchMakerCompleteHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] MatchMakerCompleteHandler")

        ## incoming match_json
        match_json = self.request.get('match_json')
        ## incoming firebaseUser
        firebaseUser = self.request.get('firebaseUser')

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}


        #try:
        URL = "%s/user/%s/matchmaker/complete" % (HEROKU_SOCKETIO_SERVER, firebaseUser)
        resp, content = http_auth.request(URL,
                            ##"PATCH",
                          "PUT", ## Write or replace data to a defined path,
                          match_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)
        #except:
        #    logging.error('Heroku Error')
