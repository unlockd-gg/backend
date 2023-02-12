import endpoints
import logging
import uuid
import urllib
import json
import math
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

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GameServerClusterManagerHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameServerClusterManagerHandler")

        ## this is a server cluster key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        gamesController = GamesController()
        serverController = ServersController()
        serverClusterController = ServerClustersController()
        serverShardController = ServerShardsController()
        serverShardPlaceholderController = ServerShardPlaceholderController()

        server_cluster = serverClusterController.get_by_key_id(int(key_id))
        if not server_cluster:
            logging.info('server cluster not found')
            return

        ## Stop if the developer has turned the task off
        if server_cluster.server_manager_task_should_stop:
            logging.info('Stopping task because it is not enabled in developer server cluster')
            return;

        game = gamesController.get_by_key_id(server_cluster.gameKeyId)
        if not game:
            logging.info('game not found')
            return

        ## Before working on any processing, check the consecutive_unused_runs
        ## if nothing is happening, notify discord, and do not restart the task
        consecutive_unused_runs = 0
        max_consecutive_unused_runs = 10
        if self.request.get('consecutive_unused_runs'):
            try:
                consecutive_unused_runs = int(self.request.get('consecutive_unused_runs'))
            except:
                logging.info('could not convert consecutive_unused_runs')

        if consecutive_unused_runs >= max_consecutive_unused_runs:
            logging.info('max_consecutive_unused_runs exceeded')

            server_cluster.server_manager_task_running = False
            serverClusterController.update(server_cluster)

            if game.discord_subscribe_server_manager_status and game.discord_webhook_admin:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "SERVER CLUSTER MANAGER: Exceeded max consecutive unused runs.  Shutting Down.  Restart via the uetopia server cluster screen" 
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Shard Manager Shutting Down", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord error')

            return






        ###########
        ## First check to see if there are any reservation requests with server assigned pending on this cluster
        ## These would have been issued to a player requesting to join a sharded server in Find Sessions
        ##  -- in FInd Sessions we already figured out How many shards are currently online? and How much available space do they have? then assigned the user to one of them
        ## Check to see if any of these are out of date or stale.
        ## -- they should get deleted when a player connects to the server successfully
        ## -- But might not in the case of a user stopping matchmaker or some type of network error
        ##
        ## Next check for any reservation requests that are not server assigned.
        ## these would be created when a player does find sessions, and there is not enough room on any server to immediately join.
        ## We shouldn't need to recalculate avaialbe space here.  we just assume they are full.
        ## figure out how many servers are needed to accomoodate the number of requests, them create those servers - assigning the reservations to the new server.

        ##  FIrst step
        stale_placeholder_count = 0
        staleDateTime = datetime.datetime.now() - SERVER_CLUSTER_MANAGER_PLACEHOLDER_STALE_TIME
        stale_placeholders = serverShardPlaceholderController.get_stale_by_serverClusterKeyId(server_cluster.key.id(), staleDateTime)
        for stale_placeholder in stale_placeholders:
            logging.info('found a stale placeholder')

            chat_message = "Your shard placeholder went stale.  There may have been an error.  Please retry your connection attempt. "
            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': stale_placeholder.firebaseUser,
                                                                                "message": chat_message,
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })
            serverShardPlaceholderController.delete(stale_placeholder)

            stale_placeholder_count = stale_placeholder_count +1

        if stale_placeholder_count > 0:
            if game.discord_subscribe_server_manager_status and game.discord_webhook_admin:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "STALE PLACEHOLDERS DELETED: %s " % ( stale_placeholder_count )
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Shard Manager Status", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord error')



        ##  Second step

        ## we need the server templates that can be sharded first, then we can look for the unassigned placeholders

        logging.info('looking for sharded servers')

        total_shards_created = 0

        server_shard_templates = serverController.list_sharded_server_template_serverClusterKeyId( server_cluster.key.id() )

        for server_shard_template in server_shard_templates:
            logging.info('found server shard template')




            unassigned_placeholders = serverShardPlaceholderController.get_not_ServerAssigned_by_serverShardTemplateKeyId( server_shard_template.key.id() )

            ## keep track of the results of the operation total per shard template
            shards_created = 0
            placeholders_unassigned = len(unassigned_placeholders)

            ## NO NEED TO count how many sever spots are available.  IF WE ARE HERE, the servers are full and we need more.

            number_of_slots_per_server = server_shard_template.sharded_player_capacity_threshold
            number_of_servers_needed = int(math.ceil(float(len(unassigned_placeholders) ) / number_of_slots_per_server) )

            ## get the list of previously created shards
            previously_created_shards = serverShardController.get_list_by_serverShardTemplateKeyId(server_shard_template.key.id())

            if number_of_servers_needed > 0:
                logging.info('need more than 0 servers')

                for serverNeededIndex in range(number_of_servers_needed):
                    logging.info('attempting to setup a server shard')

                    if server_shard_template.shard_count_maximum <= len(previously_created_shards):
                        logging.info('no more shards are permitted. ')

                        ## TODO send an error to the game discord
                        #return None
                        break

                    shards_created = shards_created +1
                    total_shards_created = total_shards_created +1

                    shard_identifier = len(previously_created_shards) + 1
                    shard_title = "%s - %s" %(server_shard_template.title, shard_identifier)
                    ## create a new server based on the template
                    new_server_shard = serverController.create(
                        title = shard_title,
                        description = server_shard_template.description,
                        hostConnectionLink = "",
                        gameKeyId = server_shard_template.gameKeyId,
                        gameTitle = server_shard_template.gameTitle,
                        admissionFee = server_shard_template.admissionFee,
                        apiKey = serverController.create_unique_api_key(),
                        apiSecret = serverController.key_generator(),
                        session_host_address = "1234",
                        session_id = "1234",
                        ## moved to server cluster
                        #continuous_server_project = server.continuous_server_project,
                        #continuous_server_bucket = server.continuous_server_bucket,
                        #continuous_server_region = server.continuous_server_region,
                        #continuous_server_zone = server.continuous_server_zone,
                        #continuous_server_source_disk_image = server.continuous_server_source_disk_image,
                        #continuous_server_machine_type = server.continuous_server_machine_type,
                        #continuous_server_startup_script_location = server.continuous_server_startup_script_location,
                        #continuous_server_shutdown_script_location = server.continuous_server_shutdown_script_location,
                        maxActiveUsers = server_shard_template.maxActiveUsers,
                        maxAuthorizedUsers = server_shard_template.maxAuthorizedUsers,
                        userKeyId = server_shard_template.userKeyId,
                        minimumCurrencyHold = server_shard_template.minimumCurrencyHold,
                        totalCurrencyHeld = 0,
                        incrementCurrency = 0,
                        currencyAwarded = 0,
                        serverCurrency = 0,
                        serverAdminPaid = False,
                        disableAdminPayment = False,
                        invisible = False,
                        invisible_developer_setting = False,
                        continuous_server = True,
                        continuous_server_creating = False,
                        continuous_server_provisioned = False,
                        continuous_server_active = False,
                        continuous_server_entry = False, ## we don't want shards coming up in the random entry query
                        serverClusterKeyId = server_shard_template.serverClusterKeyId,
                        gameLevelKeyId = server_shard_template.gameLevelKeyId,
                        gameLevelTitle = server_shard_template.gameLevelTitle,

                        vendors_allowed = server_shard_template.vendors_allowed,
                        player_created_vendors_allowed = server_shard_template.player_created_vendors_allowed,

                        ## SHARDED SERVER SPECIFICS
                        sharded_server_template = False,
                        sharded_from_template = True,
                        sharded_from_template_serverKeyId = server_shard_template.key.id(),
                        sharded_from_template_serverTitle = server_shard_template.title,

                        #instanced_for_groupKeyId = ndb.StringProperty(indexed=True)
                        #instanced_for_groupTitle = ndb.StringProperty(indexed=False)
                        server_to_game_transfer_threshold = server_shard_template.server_to_game_transfer_threshold,
                        server_to_game_transfer_exceeded = server_shard_template.server_to_game_transfer_exceeded,

                        ## Custom server configuration settings, whioch can be changed inside the server itself
                        configuration = server_shard_template.configuration,

                        drop_items_permitted = server_shard_template.drop_items_permitted,
                        pickup_items_permitted = server_shard_template.pickup_items_permitted,

                        # require badge tags to play on this server
                        requireBadgeTags = server_shard_template.requireBadgeTags

                    )

                    server_shard_record = serverShardController.create(
                        serverShardTemplateKeyId = server_shard_template.key.id(),
                        serverShardTemplateTitle = server_shard_template.title,

                        serverShardKeyId = new_server_shard.key.id(),
                        serverShardTitle = new_server_shard.title,

                        gameKeyId = server_shard_template.gameKeyId,
                        gameTitle = server_shard_template.gameTitle,

                        serverClusterKeyId = server_shard_template.serverClusterKeyId,
                        #serverClusterTitle = ndb.StringProperty(indexed=False)

                        playerCount = 0,
                        playerCapacityThreshold = server_shard_template.sharded_player_capacity_threshold,
                        playerCapacityMaximum = server_shard_template.sharded_player_capacity_maximum,

                        online = False,
                        shardId = shard_identifier
                    )

                    ## set up the chat channel
                    server_chat_title = new_server_shard.title + " chat"
                    chat_channel = ChatChannelsController().create(
                        title = server_chat_title,
                        #text_enabled = True,
                        #data_enabled = False,
                        channel_type = 'server',
                        #adminUserKeyId = authorized_user.key.id(),
                        refKeyId = new_server_shard.key.id(),
                        max_subscribers = 200
                    )

                    ## assign as many the placeholders as will fit.

                    for placeholderindex in range(number_of_slots_per_server):
                        logging.info('assigning the new server to the placeholder')

                        if len(unassigned_placeholders) > 0:

                            unassigned_placeholder = unassigned_placeholders.pop(0) ## take one from the bottom

                            unassigned_placeholder.serverShardKeyId = new_server_shard.key.id()
                            unassigned_placeholder.serverShardTitle = new_server_shard.title
                            unassigned_placeholder.serverAssigned = True

                            serverShardPlaceholderController.update(unassigned_placeholder)

                    ## Start the task to bring up the new server
                    taskUrl='/task/server/vm/allocate'
                    taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                            "serverKeyId": new_server_shard.key.id()
                                                                                        })



            ## update discord with the status of the task per server (still within the for loop)

            if shards_created > 0:
                if game.discord_subscribe_server_manager_status and game.discord_webhook_admin:
                    try:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "SERVER: %s Shards Created: %s | Placeholders: %s" % ( server_shard_template.title, shards_created, placeholders_unassigned)
                        url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                        discord_data = { "embeds": [{"title": "Shard Manager Status", "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)
                    except:
                        logging.info('discord error')


        ## requeue the task

        if total_shards_created > 0:
            logging.info('requeueing task')
            taskUrl='/task/game/servercluster/shardmanager'
            taskqueue.add(url=taskUrl, queue_name='taskServerManager', params={'key_id': server_cluster.key.id()
                                                                                }, countdown=30)
        else:
            logging.info('requeueing task with unused count')
            taskUrl='/task/game/servercluster/shardmanager'
            taskqueue.add(url=taskUrl, queue_name='taskServerManager', params={'key_id': server_cluster.key.id(), 'consecutive_unused_runs': consecutive_unused_runs+1
                                                                                }, countdown=30)
