import logging
import datetime
import string
import json
from google.appengine.datastore.datastore_query import Cursor
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.game_data import GameDataController

from configuration import *

class GetDataListHandler(BaseHandler):
    def post(self):
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

            if self.request.get('cursor'):
                curs = Cursor(urlsafe=self.request.get('cursor'))
            else:
                curs = Cursor()


            entities, cursor, more = gameDataController.list_page_by_gameKeyId(server.gameKeyId, start_cursor=curs)

            return_list = []
            for entity in entities:
                return_list.append(entity.to_json())

            if cursor:
                cursor_urlsafe = cursor.urlsafe()
            else:
                cursor_urlsafe = None

            return self.render_json_response(
                authorization = True,
                success = True,
                data_list = return_list,
                cursor = cursor_urlsafe,
                more = more
            )
