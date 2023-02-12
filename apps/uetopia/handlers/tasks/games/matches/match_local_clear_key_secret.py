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

class MatchLocalClearKeySecretHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] MatchLocalClearKeySecretHandler")

        ## incoming match_key
        match_key = self.request.get('key_id')

        matchController = MatchController()

        match = matchController.get_by_key_id(int(match_key))
        if not match:
            logging.error('match not found with the specified key')
            return

        match.apiKey = None
        match.apiSecret = None

        matchController.update(match)
