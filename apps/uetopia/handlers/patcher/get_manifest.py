import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from apps.uetopia.controllers.games import GamesController

from configuration import *

class GetManifestHandler(BaseHandler):
    def get(self, gameKeyId):
        """
        Get patch manifest for a game
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """
        gameController = GamesController()

        game = gameController.get_by_key_id(int(gameKeyId))

        if not game:
            logging.info('game not found')
            return self.render_json_response(
                authorization = False,
                success = False,
            )
        else:
            logging.info('found game success')

            if not game.patcher_enabled:
                logging.info('patcher disabled')
                return self.render_json_response(
                    authorization = False,
                    success = False,
                )

            return self.render_xml_response(
                game.patcher_details_xml
            )
