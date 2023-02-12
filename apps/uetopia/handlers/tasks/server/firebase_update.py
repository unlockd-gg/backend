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
from apps.uetopia.controllers.server_shards import ServerShardsController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ServerUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ServerUpdateFirebaseHandler")

        ## this is a game key
        key_id = self.request.get('key_id')

        entity = ServersController().get_by_key_id(int(key_id))
        if not entity:
            logging.error('Server not found')
            return

        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        ## get the game
        game = GamesController().get_by_key_id(entity.gameKeyId)
        if not game:
            logging.error('Game not found')
            return

        ## count active players
        server_players = ServerPlayersController().get_list_active_by_server(entity.key.id())
        entity.active_player_count = len(server_players)

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        entity_json = json.dumps(entity.to_json())
        headers = {"Content-Type": "application/json"}

        ## if this is a shard, we need to treat it differently
        if entity.sharded_from_template:
            logging.info('this is a shard')
            serverShardController = ServerShardsController()
            server_shard = serverShardController.get_by_serverShardKeyId(entity.key.id())
            if server_shard:
                server_shard.playerCount = len(server_players)
                serverShardController.update(server_shard)

                URL = "https://ue4topia.firebaseio.com/servers/%s/shards/%s.json" % (server_shard.serverShardTemplateKeyId, entity.key.id())
                resp, content = http_auth.request(URL,
                                  "PATCH",  ## We can update specific children at a location without overwriting existing data using a PATCH request.
                                  entity_json,
                                  headers=headers)
        ## Instances also get treated differently.  Ifnoring them for now.
        ## TODO - figure out a good way to implement this.
        elif entity.instanced_from_template:
            logging.info('found instanced server - ignoring')
        else:
            #if not game.invisible:
            URL = "https://ue4topia.firebaseio.com/games/%s/clusters/%s/servers/%s.json" % (entity.gameKeyId, entity.serverClusterKeyId, entity.key.id())
            resp, content = http_auth.request(URL,
                              "PATCH",  ## We can update specific children at a location without overwriting existing data using a PATCH request.
                              entity_json,
                              headers=headers)

        ## ALL servers regardless of type get a server record.
        extended_json = json.dumps(entity.to_json_extended())

        if not entity.invisible:
            if not entity.invisible_developer_setting:

                URL = "https://ue4topia.firebaseio.com/servers/%s.json" % (entity.key.id())
                resp, content = http_auth.request(URL,
                                  "PATCH", ## We can update specific children at a location without overwriting existing data using a PATCH request.
                                  ## Named children in the data being written with PATCH will be overwritten, but omitted children will not be deleted.
                                  extended_json,
                                  headers=headers)

        return
