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

from apps.uetopia.controllers.server_clusters import ServerClustersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ServerClusterUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ServerClusterUpdateFirebaseHandler")

        ## this is a servercluster key
        key_id = self.request.get('key_id')

        ## we also need the gameKeyId
        gameKeyId = self.request.get('gameKeyId')

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}
        URL = "https://ue4topia.firebaseio.com/games/%s/clusters/%s.json" % (gameKeyId, key_id )


        entity = ServerClustersController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Server Cluster not found')

            ## delete it from firebase.
            logging.info('deleting the cluster from firebase')
            resp, content = http_auth.request(URL,
                              "DELETE", ## We can delete data with a DELETE request
                              ({}),
                              headers=headers)

            return



        entity_json = json.dumps(entity.to_json())

        #logging.info(model_json)

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
