import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_shards import ServerShardsController

from configuration import *

class GetLinksHandler(BaseHandler):
    def post(self):
        """
        Get connected links for a server
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """
        serverController = ServersController()
        serverLinksController = ServerLinksController()
        serverShardController = ServerShardsController()

        server = serverController.verify_signed_auth(self.request)


        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            ## instanced servers should get server links from the parent server
            if server.instanced_from_template:
                server_links = serverLinksController.get_list_by_originServerKeyId(server.instanced_from_template_serverKeyId)
            ## same with sharded servers
            elif server.sharded_from_template:
                server_links = serverLinksController.get_list_by_originServerKeyId(server.sharded_from_template_serverKeyId)
            else:
                server_links = serverLinksController.get_list_by_originServerKeyId(server.key.id())

            server_links_response = []

            for s_link in server_links:
                server_links_response.append(s_link.to_json())

            server_shards = []
            if server.sharded_from_template:
                server_shards = serverShardController.get_list_by_serverShardTemplateKeyId(server.sharded_from_template_serverKeyId)


            server_shards_response = []

            for s_shard in server_shards:
                ## skip self
                if s_shard.serverShardKeyId != server.key.id():
                    server_shards_response.append(s_shard.to_json())



            logging.info(server_links_response)


            return self.render_json_response(
                authorization = True,
                success = True,
                links = server_links_response,
                shards = server_shards_response
            )
