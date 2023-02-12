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

from apps.uetopia.controllers.users import UsersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

### THIS IS CURRENTLY UNUSED.  IT IS SAFE TO DELETE

class TransactionUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] TransactionUpdateFirebaseHandler")


        firebaseUser = self.request.get('firebaseUser')
        currentBalance = int(self.request.get('currentBalance'))


        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        transaction_json = json.dumps({
            u'currencyBalance': currentBalance
        })

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/users/%s.json" % firebaseUser
        resp, content = http_auth.request(URL,
                          "PATCH", ## Only update included items
                          transaction_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        return
