import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.utilities.server_player_deactivate import deactivate_player, deactivate_player2
from configuration import *

class DeactivateStalePlayersHandler(BaseHandler):
    def get(self):
        logging.info('Cron Deactivate Stale Players')
        spmController = ServerPlayersController()

        modified_date = datetime.datetime.now() - ACTIVE_SERVER_PLAYER_MEMBER_AUTO_EXPIRE_TIME

        expired_server_players = spmController.get_active_stale(modified_date)

        for server_player in expired_server_players:

            #deactivate_player(server_player, None, None)
            deactivate_player2(server_player, None)

        playercount = len(expired_server_players)

        return self.render_json_response(
            playercount= playercount
        )
