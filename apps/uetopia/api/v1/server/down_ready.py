import logging
import os
import datetime
import string
import uuid
import json
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from httplib2 import Http
from google.appengine.api import urlfetch

from apps.handlers import BaseHandler
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.game_levels import GameLevelsController
from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class DownReadyHandler(BaseHandler):
    def post(self):
        """
        The server is done.  It's ready to be deallocated.
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        Optional POST parameters:  session_host_address, session_id
        """

        serverController = ServersController()
        serverClusterController = ServerClustersController()
        serverPlayerController =ServerPlayersController()
        ucontroller = UsersController()
        serverLinksController = ServerLinksController()
        chatChannelsController = ChatChannelsController()
        GameLevelController = GameLevelsController()
        gameController = GamesController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            ## parse the incoming json
            jsonstring = self.request.body
            logging.info(jsonstring)
            jsonobject = json.loads(jsonstring)

            if "configuration" in jsonobject:
                logging.info('found configuration in json')
                server.configuration = jsonobject["configuration"]

            server.server_last_running_timestamp = datetime.datetime.now()

            serverController.update(server)

            ## check for active players
            active_players = serverPlayerController.get_list_active_by_server(server.key.id())
            if len(active_players) >0:
                logging.info('found active players!')

                ## get the game

                game = gameController.get_by_key_id(server.gameKeyId)

                if game:
                    if game.discord_subscribe_errors and game.discord_webhook_admin:

                        ## get the server cluster
                        server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)
                        if server_cluster:
                            http_auth = Http()
                            headers = {"Content-Type": "application/json"}
                            message = "Server reported down ready, but there were still active players found: %s | %s" % ( server.title, server_cluster.vm_zone)
                            url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                            discord_data = { "embeds": [{"title": "Server down ready error", "url": url, "description": message}] }
                            data=json.dumps(discord_data)
                            resp, content = http_auth.request(game.discord_webhook_admin,
                                              "POST",
                                              data,
                                              headers=headers)
                ## set active players to inactive

                for active_player in active_players:
                    logging.info('deactivating player')
                    active_player.active = False
                    serverPlayerController.update(active_player)


                ## run the check unused task
                ## start a task to check on the server after our timer
                taskUrl='/task/server/vm/checkunused'
                taskqueue.add(url=taskUrl, queue_name='serverCheckUnused', params={"serverKeyId": server.key.id()
                                                                                    }, countdown=120)






            return self.render_json_response(
                authorization = True,

            )
