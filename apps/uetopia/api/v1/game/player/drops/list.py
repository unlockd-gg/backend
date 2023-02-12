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

class dropListHandler(BaseHandler):
    def post(self):
        """
        Send game player
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

        ## parse the incoming json
        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        ## get the gamePlayer
        if 'userKeyId' in jsonobject :
            logging.info('found userKeyId')

        game_player = gpController.get_by_gameKeyId_userKeyId(game.key.id(), int(jsonobject['userKeyId']))
        if not game_player:
            logging.info('game_player not found')
            return self.render_json_response(
                authorization = True,
                error= "The game_player was not found."
                )


        ## get the drops
        drops = dropController.get_by_gamePlayerKeyId(game_player.key.id())

        drops_response = []

        for drop in drops:
            drops_response.append(drop.to_json())

        logging.info(drops_response)


        return self.render_json_response(
            authorization = True,
            success = True,
            drops = drops_response,
            gamePlayerKeyId = str(game_player.key.id()),
            userKeyId = str(game_player.userKeyId)
        )
