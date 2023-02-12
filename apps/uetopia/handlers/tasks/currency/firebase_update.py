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

from apps.uetopia.controllers.currency import CurrencyController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class CurrencyUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] CurrencyUpdateFirebaseHandler")



        cController = CurrencyController()

        db_currency = cController.get_by_iso_code("BTC")

        if not db_currency:
            logging.error('BTC not found')
            return

        currency_json = json.dumps(db_currency.to_json())

        #logging.info(model_json)
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())

        headers = {"Content-Type": "application/json"}
        URL = "https://ue4topia.firebaseio.com/currency/CRED.json"
        resp, content = http_auth.request(URL,
                            "PATCH",
                          ##"PUT", ## Write or replace data to a defined path,
                          currency_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        return
