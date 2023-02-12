import logging
import datetime
import string
import json
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.game_player_snapshot import GamePlayerSnapshotController
from apps.uetopia.utilities.game_player_snapshot import create_game_player_snapshot
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.drops import DropsController
from configuration import *

class dropClaimHandler(BaseHandler):
    def post(self, dropKeyId):
        """
        Claim a Drop
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        Optional parameters:  unlock
        """

        ## This request could be coming in from a server
        ## OR, a match...
        ## we need to check for both.

        serverController = ServersController()
        ucontroller = UsersController()
        gpController = GamePlayersController()
        gameController = GamesController()
        #gameCharacterController = GameCharactersController()
        #gamePlayerSnapshotController = GamePlayerSnapshotController()

        matchController = MatchController()
        dropController = DropsController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        game = None
        match = None

        if server:
            logging.info('auth success')
            game = gameController.get_by_key_id(server.gameKeyId)

        else:
            logging.info('auth failure using server')

            match = matchController.verify_signed_auth(self.request)

            if match:
                logging.info('auth success using match')
                game = gameController.get_by_key_id(match.gameKeyId)

        if not game:
            logging.info('game not found')
            return self.render_json_response(
                authorization = True,
                error= "The game was not found."
                )

        ## get the drop
        drop = dropController.get_by_key_id(int(dropKeyId))

        if drop.gameKeyId != game.key.id():
            logging.info('This drop is not a part of this game')
            return self.render_json_response(
                authorization = True,
                error= "The drop was not found."
                )

        ## delete it
        dropController.delete(drop)

        return self.render_json_response(
            authorization = True,
            success = True,
            title = drop.title,
            description = drop.description,
            userKeyId = drop.userKeyId,
            uiIcon = drop.uiIcon,
            data = drop.data,
            tier = drop.tier
        )
