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

class TaskServerDeactivateAll(BaseHandler):
    """
    Deauthorize all players on a server

    """
    def post(self):
        """

        """
        ## this is a server key
        server_key_id = int(self.request.get('key_id'))

        serverController = ServersController()
        uController = UsersController()
        spController = ServerPlayersController()

        server = serverController.get_by_key_id(server_key_id)

        ## get all server players that are active

        server_players = spController.get_list_authorized_by_server(server.key.id())

        for server_player in server_players:
            logging.info('found an authorized player on this server')
            server_player.active = False
            server_player.admission_paid = False
            spController.update(server_player)
