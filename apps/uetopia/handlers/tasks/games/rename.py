import endpoints
import logging
import uuid
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

#from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_levels import GameLevelsController
from apps.uetopia.controllers.game_level_links import GameLevelLinksController
from apps.uetopia.controllers.game_data import GameDataController
from apps.uetopia.controllers.group_games import GroupGamesController

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController


from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GameRenameHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameRenameHandler")

        ## this is a game key
        key_id = self.request.get('key_id')

        userController = UsersController()

        gamesController = GamesController()
        gameModesController = GameModesController()
        gamePlayersController = GamePlayersController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()
        gameDataController = GameDataController()
        groupGameController = GroupGamesController()

        serversController = ServersController()
        serverClustersController = ServerClustersController()
        serverLinksController = ServerLinksController()
        serverPlayersController = ServerPlayersController()

        transactionController = TransactionsController()
        lockController = TransactionLockController()

        game = gamesController.get_by_key_id(int(key_id))
        if not game:
            logging.error('Game not found')
            return

        ## Inside of rename, we're going to need sub-tasks to handle batching
        ## gamePlayers
        taskUrl='/task/game/players/game_batch_rename'
        taskqueue.add(url=taskUrl, queue_name='gameRenameSubprocess', params={'key_id': game.key.id()})

        ## groupGames
        taskUrl='/task/group/game_batch_rename'
        taskqueue.add(url=taskUrl, queue_name='gameRenameSubprocess', params={'key_id': game.key.id()})

        ## servers
        taskUrl='/task/server/game_batch_rename'
        taskqueue.add(url=taskUrl, queue_name='gameRenameSubprocess', params={'key_id': game.key.id()})

        ## serverPlayers - I think we can skip this one,  Seems like it's never really referenced.

        ## The records we can update as a one-shot are:
        # game data
        # game Level links
        # game levels
        # game modes
        ## but none of these should be referenced at all using gameTitle
