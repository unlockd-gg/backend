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

class GameDeleteHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameDeleteHandler")

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

        developer_user = userController.get_by_key_id(game.userKeyId)
        if not developer_user:
            logging.error('developer_user not found')
            return

        ## delete all of the child data first
        # game level links
        # game levels
        # game modes
        # game players

        ##  game data
        ## group games

        # loop over the game's servers and delete child data
        # server players
        # server links
        # server clusters

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        entity_json = json.dumps(game.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/games/%s" % (game.key.id())
        resp, content = http_auth.request(URL,
                          "DELETE", ## Write or replace data to a defined path,
                          entity_json,
                          headers=headers)


        group_games = groupGameController.get_by_gameKeyId(game.key.id())
        for group_game in group_games:
            logging.info('found and deleted a group game')
            groupGameController.delete(group_game)

        game_datas = gameDataController.list_by_gameKeyId(game.key.id())
        for game_data in game_datas:
            logging.info('found and deleted a game data')
            gameDataController.delete(game_data)

        gls = gameLevelsController.list_by_gameKeyId(game.key.id())
        for gl in gls:

            glls = gameLevelLinksController.list_by_gameLevelKeyId(gl.key.id())
            for gll in glls:
                logging.info('found and deleted a game level link')
                gameLevelLinksController.delete(gll)

            logging.info('found and deleted a game level')
            gameLevelsController.delete(gl)

        gps = gamePlayersController.get_by_gameKeyId(game.key.id())  ## TODO handle more than 100 users.  subtask(s)?
        for gp in gps:
            logging.info('found and deleted a game player')

            URL = "https://ue4topia.firebaseio.com/users-public/%s/games/%s.json" % (gp.userKeyId, game.key.id())
            resp, content = http_auth.request(URL,
                              "DELETE", ## Remove it
                              entity_json,
                              headers=headers)

            gamePlayersController.delete(gp)

        gms = gameModesController.get_by_gameKeyId(game.key.id())
        for gm in gms:
            logging.info('found and deleted a game mode')
            gameModesController.delete(gm)

        scs, cursor, more = serverClustersController.list_page_by_gameKeyId(game.key.id())
        for sc in scs:
            logging.info('found and deleted a server cluster')
            serverClustersController.delete(sc)

        ##  deal with cred?
        currency_transfarred_from_servers = 0

        gss = serversController.get_by_gamekeyid(game.key.id())
        for gs in gss:
            currency_transfarred_from_servers = currency_transfarred_from_servers + gs.serverCurrency
            sps = serverPlayersController.get_list_by_server(gs.key.id())
            for sp in sps:
                logging.info('found and deleted a server player')
                serverPlayersController.delete(sp)

            sls = serverLinksController.get_list_by_originServerKeyId(gs.key.id())
            for sl in sls:
                logging.info('found and deleted a server link')
                serverLinksController.delete(sl)

            logging.info('found and deleted a server')
            serversController.delete(gs)

        if game.currencyBalance:
            total_currency_to_transfer = game.currencyBalance + currency_transfarred_from_servers
        else:
            total_currency_to_transfer = currency_transfarred_from_servers

        logging.info('total currency to transfer: %s' %total_currency_to_transfer)

        ## currency is going to go back to the developer listed.
        if total_currency_to_transfer > 0:
            description = "Game Deletion: %s" %game.title
            recipient_transaction = transactionController.create(
                amountInt = total_currency_to_transfer,
                ##amount = ndb.FloatProperty(indexed=False) # for display
                ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                ##newBalance = ndb.FloatProperty(indexed=False) # for display
                description = description,
                userKeyId = developer_user.key.id(),
                firebaseUser = developer_user.firebaseUser,
                ##targetUserKeyId = ndb.IntegerProperty()
                gameKeyId = game.key.id(),
                gameTitle = game.title,

                ##  transactions are batched and processed all at once.
                transactionType = "user",
                transactionClass = "game deletion",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_DELETE,
                materialDisplayClass = "md-primary"
            )


        ## only start pushable tasks.  If they are not pushable, there is already a task running.
        pushable = lockController.pushable("user:%s"%developer_user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": developer_user.key.id()
                                                                                }, countdown=2)

        gamesController.delete(game)

        ## deleting from firebase too
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        game_json = json.dumps(game.to_json())
        headers = {"Content-Type": "application/json"}
        URL = "https://ue4topia.firebaseio.com/games/%s.json" % game.key.id()

        resp, content = http_auth.request(URL,
                      "DELETE", ## We can delete data with a DELETE request
                      game_json,
                      headers=headers)
