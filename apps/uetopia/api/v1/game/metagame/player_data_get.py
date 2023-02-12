import logging
import datetime
import string
import json
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.providers.compute_engine_zonemap import region_zone_mapper
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController
from configuration import *

class playerDataGetHandler(BaseHandler):
    def post(self):
        """
        Get a player
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, playerKeyId
        """

        serverController = ServersController()
        ucontroller = UsersController()
        gpController = GamePlayersController()
        gameController = GamesController()
        #gamePlayerSnapshotController = GamePlayerSnapshotController()
        gamePlayerController = GamePlayersController()

        try:
            game = gameController.verify_signed_auth(self.request)
        except:
            game = False

        if game == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                request_successful = False
            )
        else:
            logging.info('auth success')

        logging.info(self.request)


        # get the game player
        game_player = gamePlayerController.get_by_key_id(int(self.request.get('playerKeyId')))
        if not game_player:
            logging.info('did not find game_player')
            return self.render_json_response(
                authorization = True,
                error= "The game player was not found.",
                request_successful = False
                )

        # make sure the game matches this player

        if game_player.gameKeyId != game.key.id():
            logging.info('game_player did not match the game')
            return self.render_json_response(
                authorization = True,
                error= "The game player is not from this game.",
                request_successful = False
                )

        ## TODO - any other checks?
        return self.render_json_response(
            authorization = True,
            gamePlayerKeyId = game_player.key.id(),
            rank = game_player.rank,
            score = game_player.score,
            experience = game_player.experience,
            level = game_player.level,
            inventory = game_player.inventory,
            equipment = game_player.equipment,
            abilities = game_player.abilities,
            interface = game_player.interface,
            crafting = game_player.crafting,
            recipes = game_player.recipes,
            character = game_player.character,
            request_successful = True
            )
