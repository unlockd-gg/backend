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
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_instances import ServerInstancesController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController


from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class PatchApplyHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] PatchApplyHandler")

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

        serverController = ServersController()
        serverShardController = ServerShardsController()
        serverInstancesController = ServerInstancesController()
        serverClusterController = ServerClustersController()
        serverLinksController = ServerLinksController()
        serverPlayersController = ServerPlayersController()

        transactionController = TransactionsController()
        lockController = TransactionLockController()

        game = gamesController.get_by_key_id(int(key_id))
        if not game:
            logging.error('Game not found')
            return



        ## Get all of the servers
        ## we want to check even the ones that are supposedly offline.
        all_game_servers = serverController.get_by_gamekeyid(game.key.id())
        for server in all_game_servers:
            logging.info('found a server')

            ## only do this if it is LIVE.  Ignore localhost servers
            if server.continuous_server:
                logging.info('This server is LIVE')

                ## if it is active, create an instance report for billing

                ## if this is a sharded or instanced server, use the parent server's ket/title
                if server.instanced_from_template:
                    wallet_server_key_id = server.instanced_from_template_serverKeyId
                    wallet_server_title = server.instanced_from_template_serverTitle
                elif server.sharded_from_template:
                    wallet_server_key_id = server.sharded_from_template_serverKeyId
                    wallet_server_title = server.sharded_from_template_serverTitle
                else:
                    wallet_server_key_id = server.key.id()
                    wallet_server_title = server.title

                ## It is possible that the server is marked as online, but was not actually created via that VM allocation process
                ## If so, it won't have a created datetime.
                ## So, we just skip this part.

                if server.continuous_server_creating_timestamp:
                    logging.info('found server.continuous_server_creating_timestamp')

                    created_datetime = server.continuous_server_creating_timestamp

                    destroying_datetime = datetime.datetime.now()
                    total_seconds = (destroying_datetime - created_datetime).total_seconds()
                    if total_seconds < VM_INSTANCE_MINIMUM_SECONDS:
                        total_seconds = VM_INSTANCE_MINIMUM_SECONDS

                    ## round up
                    billable_min_uptime = int((total_seconds+(-total_seconds%60))//60)

                    serverInstance = serverInstancesController.create(
                        serverKeyId = wallet_server_key_id,
                        serverTitle = wallet_server_title,

                        machine_type = server_cluster.vm_machine_type,
                        region_name = server_cluster.vm_region,

                        continuous_server_creating_timestamp = created_datetime,
                        continuous_server_destroying_timestamp = destroying_datetime,

                        uptime_minutes_billable = billable_min_uptime,

                        serverClusterKeyId = server.serverClusterKeyId,
                        ##serverClusterTitle = server.serverClusterTitle,

                        userKeyId = server.userKeyId,
                        gameKeyId = server.gameKeyId,
                        processed = False,
                        instanceType = 'server'
                    )



                ## Do modified  server deallocation routine
                ## - since all servers are coming down, we can do everything in bulk, without all of the individual link checks.

                ## Here we want to set the active flag to false so that the deallocation process knows that we are done with it.
                ## Also turn off the old IP and connection link
                server.continuous_server_active = False
                server.continuous_server_provisioned = False
                server.continuous_server_creating = False
                server.continuous_server_creating_timestamp = None
                server.continuous_server_destroying_timestamp = datetime.datetime.now()
                server.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
                server.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
                server.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value
                serverController.update(server)

                ## send each a GC deallocate message.
                ## get the server cluster so we can get the VM info
                server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)

                ## Start a task to deactivate all players from this server
                taskUrl = '/task/server/player/deactivate_all'
                taskqueue.add(url=taskUrl, queue_name='taskGamePatcher', params={'key_id': server.key.id()
                                                                                    }, countdown=2)


                ## start a task to dealoocate the VM
                taskUrl='/task/server/vm/deallocate'
                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': server_cluster.vm_project,
                                                                                        "zone": server_cluster.vm_zone,
                                                                                        "name": server.continuous_server_title,
                                                                                        "serverKeyId": server.key.id()
                                                                                    }, countdown=2)

        ## reset all shard records
        all_game_shards = serverShardController.get_by_gameKeyId(game.key.id())

        for shard in all_game_shards:
            shard.online = False
            shard.playerCount = 0
            serverShardController.update(shard)

        ## reset all links
        all_game_links = serverLinksController.get_by_gameKeyId(game.key.id())
        for link in all_game_links:
            link.hostConnectionLink = "None"
            link.targetStatusProvisioned = False
            link.targetStatusOnline = False

            serverLinksController.update(link)



        ## move the temporary patch data into the game and server containers
        curs = Cursor()
        more = True
        while more:
            all_server_clusters, curs, more = serverClusterController.list_page_by_gameKeyId(game.key.id(), start_cursor=curs)
            logging.info('checking for server clusters')

            for server_cluster in all_server_clusters:
                logging.info('found a server cluster')

                server_cluster.vm_disk_image = game.patcher_server_disk_image
                serverClusterController.update(server_cluster)

        game.patcher_patching = False;

        game.patcher_details_xml = game.patcher_prepatch_xml
        game.patcher_prepatch_xml = None

        game.patcher_server_shutdown_seconds = 0

        game.patcher_server_shutdown_warning_chat = None

        game.match_deploy_vm_source_disk_image = game.patcher_server_disk_image
        game.patcher_server_disk_image = None

        gamesController.update(game)
