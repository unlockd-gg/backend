import logging
import re
import os
import datetime
import json
import uuid
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController

from apps.uetopia.controllers.match_results import MatchResultsController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.utilities.server_player_deactivate import deactivate_player, deactivate_player2

#from apps.uetopia.controllers.sense import SenseController

#from apps.uetopia.utilities.player.experience import process_player_experience

from configuration import *

class TaskServerDeauthorize(BaseHandler):
    """
    Deauthorize a player

    """
    def post(self):
        """

        """
        server_player_member_key_id = int(self.request.get('key_id'))

        serverController = ServersController()
        uController = UsersController()
        spController = ServerPlayersController()

        server_player = spController.get_by_key_id(server_player_member_key_id)

        authenticated_user = uController.get_by_key_id(server_player.userKeyId)
        server = serverController.get_by_key_id(server_player.serverKeyId)


        logging.info("incoming server_player_member_key_id: %s" % server_player_member_key_id)


        if authenticated_user:
            logging.info('user found')

            user_key_id = authenticated_user.key.id()

            if server_player:
                logging.info('server_player_member found')
                logging.info('server_player_member currencyCurrent: %s' % server_player.currencyCurrent)

                new_rank = self.request.get('rank', 1600)
                #currency_balance = self.request.get('currency_balance', 0)
                #deactivate_player(server_player, new_rank, currency_balance)

                deactivate_player2(server_player, new_rank, user=authenticated_user)


            else:
                logging.info('server_player_member NOT found')
                authorized = False
                auth_deny_reason = "Authorization: record missing"
