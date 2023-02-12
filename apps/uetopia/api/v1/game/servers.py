import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.server_shards import ServerShardsController

from configuration import *

class GetServersHandler(BaseHandler):
    def get(self, gameKeyId):
        """
        Get Servers for a game
        Requires http headers:  -
        Requires POST parameters:  -
        """
        serverController = ServersController()
        serverShardController = ServerShardsController()

        servers = serverController.get_provisioned_by_game_key_id(int(gameKeyId))

        servers_response = []

        for server in servers:
            ## this is not used here.  User servers are in the user_servers handler
            ##if server.sharded_from_template:
            ##    logging.info('found a shard - looking up current state')
            ##    s_shard = serverShardController.get_by_serverShardKeyId(server.key.id())
            ##    if s_shard:
            ##        logging.info('got shard data')
            ##        if s_shard.playerCount < s_shard.playerCapacityThreshold:
            ##            logging.info('this shard still has space below the threshold')
            ##            servers_response.append(server.to_json_for_session())

            ##else:
            ##    logging.info('not a sharded server - adding')

            servers_response.append(server.to_json_for_session())

        return self.render_json_response(
            authorization = True,
            success = True,
            servers = servers_response
        )
