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

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.games import GamesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ServerPlayerUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ServerPlayerUpdateFirebaseHandler")

        ## this is a server_player key
        key_id = self.request.get('key_id')
        connecting = self.request.get('connecting', 'false')
        disconnecting = self.request.get('disconnecting', 'false')

        entity = ServerPlayersController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('ServerPlayer not found')
            return

        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        ## get the server
        server = ServersController().get_by_key_id(entity.serverKeyId)
        if not server:
            logging.error('Server not found')
            return





        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        entity_json = json.dumps(entity.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}
        conditional_headers = {"Content-Type": "application/json", "X-Firebase-ETag": "true"}


        if server.sharded_from_template:
            SERVER_URL = "https://ue4topia.firebaseio.com/servers/%s/shards/%s/active_player_count.json" % (server.sharded_from_template_serverKeyId, server.key.id() )
            GAME_URL =  "https://ue4topia.firebaseio.com/games/%s/servers/%s/shards/%s/active_player_count.json" % (entity.gameKeyId, server.sharded_from_template_serverKeyId, server.key.id() )
            PLAYER_URL = "https://ue4topia.firebaseio.com/servers/%s/shards/%s/players/%s.json" % (server.sharded_from_template_serverKeyId, server.key.id(), entity.firebaseUser)
        else:
            SERVER_URL = "https://ue4topia.firebaseio.com/servers/%s/active_player_count.json" % (entity.serverKeyId)
            GAME_URL =  "https://ue4topia.firebaseio.com/games/%s/servers/%s/active_player_count.json" % (entity.gameKeyId,entity.serverKeyId)
            PLAYER_URL = "https://ue4topia.firebaseio.com/servers/%s/players/%s.json" % (entity.serverKeyId, entity.firebaseUser)

        if not server.invisible:
            if not server.invisible_developer_setting:
                ## testing - get the realtime count from firebase
                ## we don't actually need to to the incremnt up, since it gets caught by the server update firebase task anyways.
                ## we only need it for disconnect.
                if disconnecting == 'true':
                    logging.info('disconnecting')

                    logging.info('testing active_player_count read from firebase')
                    firebase_write_attempts = 0
                    #URL = "https://ue4topia.firebaseio.com/servers/%s/active_player_count.json" % (entity.serverKeyId)
                    resp, content = http_auth.request(SERVER_URL,
                                      "get", ## Write or replace data to a defined path,
                                      headers=conditional_headers)
                    logging.info(resp)
                    logging.info(content)

                    ## parse the json response
                    json_response = resp# json.loads(resp.read())
                    if json_response['status'] == '200':
                        logging.info('status 200')
                        if json_response['etag']:
                            logging.info(json_response['etag'])

                            retry_again = True
                            retry_etag = json_response['etag']

                            #URL = "https://ue4topia.firebaseio.com/servers/%s/active_player_count.json" % (entity.serverKeyId)

                            active_user_count_updated = str(int(content) -1)

                            while retry_again:
                                conditional_put_headers = {"Content-Type": "application/json", "if-match": retry_etag}
                                resp, content = http_auth.request(SERVER_URL,
                                                  "PUT", ## Write or replace data to a defined path,
                                                  active_user_count_updated,
                                                  headers=headers)
                                logging.info(resp)
                                logging.info(content)

                                ## TODO check to see if the ecode changed, and if so, retry
                                retry_again = False



                            #URL = "https://ue4topia.firebaseio.com/games/%s/servers/%s/active_player_count.json" % (entity.gameKeyId,entity.serverKeyId)
                            resp, content = http_auth.request(GAME_URL,
                                              "PUT", ## Write or replace data to a defined path,
                                              active_user_count_updated,
                                              headers=headers)

                            logging.info(resp)
                            logging.info(content)



                ## adding basic data to the parent server
                #URL = "https://ue4topia.firebaseio.com/servers/%s/players/%s.json" % (entity.serverKeyId, entity.firebaseUser)
                resp, content = http_auth.request(PLAYER_URL,
                                  "PUT", ## Write or replace data to a defined path,
                                  entity_json,
                                  headers=headers)

                ## complete data in it's own record
                extended_json = json.dumps(entity.to_json_extended())
                URL = "https://ue4topia.firebaseio.com/server_players/%s.json" % (entity.key.id())
                resp, content = http_auth.request(URL,
                                  "PATCH", ## We can update specific children at a location without overwriting existing data using a PATCH request.
                                  ## Named children in the data being written with PATCH will be overwritten, but omitted children will not be deleted.
                                  extended_json,
                                  headers=headers)

        return
