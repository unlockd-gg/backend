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
from apps.uetopia.controllers.game_data import GameDataController

from configuration import *

class GetDataHandler(BaseHandler):
    def post(self, key_id_str):
        """
        Get game data for a server
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """
        serverController = ServersController()
        serverLinksController = ServerLinksController()
        gameDataController = GameDataController()

        server = serverController.verify_signed_auth(self.request)

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                success = False,
            )
        else:
            logging.info('auth success')


            game_data = gameDataController.get_by_key_id(int(key_id_str))

            if not game_data:
                logging.info('No Game Data found with the supplied key')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                    data = "",
                )

            if game_data.gameKeyId != server.gameKeyId:
                logging.info('game data and server are not in the same game.')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                    data = "",
                )

            return self.render_json_response(
                authorization = True,
                success = True,
                data = game_data.data
            )
