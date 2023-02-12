import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.server_links import ServerLinksController
#from apps.uetopia.controllers.sense import SenseController

from configuration import *

class MountLinkHandler(BaseHandler):
    def post(self, serverKeyId):
        """
        Mount a server link
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """

        ## Check to see if the origin server has permissions
        ## Check to make sure the target server is capable of mounting
        ## start the task to bring up the VM

        serverController = ServersController()
        serverLinksController = ServerLinksController()


        server = serverController.verify_signed_auth(self.request)

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                success = False,
            )
        else:
            logging.info('auth success')


            target_server = serverController.get_by_key_id(int(serverKeyId))
            if not target_server:
                return self.render_json_response(
                    authorization = True,
                    error = "The target server could not be found.",
                    success = False,
                )

            ## get the server link
            target_server_link = serverLinksController.get_by_originServerKeyId_targetServerKeyId(server.key.id(), target_server.key.id())
            if not target_server_link:
                return self.render_json_response(
                    authorization = True,
                    error = "The server link could not be found.",
                    success = False,
                )

            if not target_server_link.permissionCanMount:
                return self.render_json_response(
                    authorization = True,
                    error = "permissionCanMount is set to False.",
                    success = False,
                )

            if target_server.continuous_server_creating:
                return self.render_json_response(
                    authorization = True,
                    error = "The target server is already being created.",
                    success = False,
                )

            if target_server.continuous_server_provisioned:
                return self.render_json_response(
                    authorization = True,
                    error = "The target server is already provisioned.",
                    success = False,
                )

            if target_server.continuous_server_active:
                return self.render_json_response(
                    authorization = True,
                    error = "The target server is already active.",
                    success = False,
                )

            ## start a task to create the vm
            taskUrl='/task/server/vm/allocate'
            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                    "serverKeyId": target_server.key.id()
                                                                                })
