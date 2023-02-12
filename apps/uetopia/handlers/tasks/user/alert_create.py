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

class UserAlertCreateHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] UserAlertCreateHandler")

        ## this is a user key
        ##key_id = self.request.get('key_id')
        firebase_user = self.request.get('firebase_user')
        icon_url = self.request.get('icon_url', None)
        material_icon = self.request.get('material_icon', None)
        importance = self.request.get('importance')
        message_text = self.request.get('message_text')
        action_button_color = self.request.get('action_button_color', None)
        action_button_sref = self.request.get('action_button_sref', None)


        ## TODO user preferences for alert levels showing up

        alert_uuid = uuid.uuid4()

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        alert_json = json.dumps({
            u'icon_url': icon_url,
            u'material_icon': material_icon,
            u'importance': importance,
            u'message_text': message_text,
            u'action_button_color': action_button_color,
            u'action_button_sref':action_button_sref
        })

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/users/%s/alerts/%s.json" % (firebase_user, alert_uuid)
        logging.info('URL: %s'%URL)
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          alert_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        return
