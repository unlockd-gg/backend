import logging
import datetime
import json
import random
import uuid
from google.appengine.api import taskqueue
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController

from configuration import *


spController = ServerPlayersController()
serverController = ServersController()
serverShardController = ServerShardsController()
serverShardPlaceholderController = ServerShardPlaceholderController()
gamePlayerController = GamePlayersController()
lockController = TransactionLockController()
transactionController = TransactionsController()
chatChannelSubscribersController = ChatChannelSubscribersController()
chatChannelController = ChatChannelsController()

teamController = TeamsController()
teamMembersController = TeamMembersController()

groupController = GroupsController()
groupUserController = GroupUsersController()
groupRoleController = GroupRolesController()
groupGameController = GroupGamesController()

chat_message_controller = ChatMessagesController()

def detect_init_shard_server(server, user, team, team_member):
    logging.info('detect_init_shard_server')

    if server.sharded_server_template:
        logging.info('Found a sharded_server_template')

        ## if the user is in a team
        if team:
            logging.info('found team')
            if not team_member.captain:
                logging.info('NOT team captain - sending a chat message')

                error_message = "Only the team captain can initiate travel."
                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": error_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                }, countdown = 0,)
                return None


            ## we need the team size
            all_team_members = teamMembersController.get_by_teamKeyId(team.key.id())
            team_size = len(all_team_members)

        else:
            team_size = 1

        ## Before doing anything else, check the placeholders...
        ## if there is a placeholder, and the server is online, just return it
        existing_placeholder = serverShardPlaceholderController.get_by_userKeyId_gameKeyId( user.key.id(), server.gameKeyId )
        if existing_placeholder:
            logging.info('found an existing placeholder')

            logging.info('existing_placeholder.serverKeyId: %s ' % existing_placeholder.serverKeyId )
            logging.info('existing_placeholder.serverShardTemplateKeyId: %s ' % existing_placeholder.serverShardTemplateKeyId )
            logging.info('existing_placeholder.serverShardKeyId: %s ' % existing_placeholder.serverShardKeyId )
            logging.info('server.key.id(): %s ' % server.key.id() )



            ## the placeholder might be different...  If it is, uhhh, what to do here?
            if existing_placeholder.serverShardTemplateKeyId == server.key.id():
                logging.info('serverShardTemplateKeyId matches server')

                ## this is a lookup to the server shard table NOT servers
                placeholder_shard = serverShardController.get_by_key_id(existing_placeholder.serverShardKeyId)

                if placeholder_shard:
                    logging.info('got shard record')

                    if placeholder_shard.online:
                        logging.info('shard is online')

                        placeholder_shard_server = serverController.get_by_key_id(placeholder_shard.serverShardKeyId)

                        return placeholder_shard_server

                    else:
                        return None ## get out of here if the placeholder is not online.
                else:
                    return None ## bail on errors
            else:
                logging.info('serverShardKeyId does not match server.key.id')
                return None


        ## get the player's most recent shards
        # look up serverplayers by servershard template key order by modified
        most_recent_server_players_on_shards = spController.get_most_recently_used_shards_by_userKeyId(server.key.id(), user.key.id())

        ## loop over the recent shards, and find the first with room
        for recent_splayer_shard in most_recent_server_players_on_shards:
            logging.info('checking server shard - from most recent for this user')

            ## this is a lookup to the server shard table NOT servers
            potential_server_shard = serverShardController.get_by_key_id(recent_splayer_shard.serverKeyId)

            ## if there is room, select this shard
            if potential_server_shard.playerCount + team_size <= server.sharded_player_capacity_threshold:
                logging.info('there seems to be room on this shard')

                ## also check placeholders

                existing_placeholders = serverShardPlaceholderController.get_serverAssigned_by_serverKeyId(potential_server_shard.serverShardKeyId)

                if potential_server_shard.playerCount + team_size + len(existing_placeholders) < server.sharded_player_capacity_threshold:
                    logging.info('there seems to be enough room after checking placeholders')

                    shard_server = serverController.get_by_key_id(recent_splayer_shard.serverShardKeyId)

                    ## set up a placeholder here
                    new_placeholder = serverShardPlaceholderController.create(
                        gameKeyId = server.gameKeyId,
                        gameTitle = server.gameTitle,
                        serverClusterKeyId = server.serverClusterKeyId,
                        serverShardTemplateKeyId = server.key.id(), ## parent
                        serverShardTemplateTitle = server.title,

                        serverShardKeyId = potential_server_shard.key.id(), ## shard
                        serverShardTitle = potential_server_shard.serverShardTitle,
                        serverAssigned = True,

                        serverKeyId = shard_server.key.id(),

                        userKeyId = user.key.id(),
                        userTitle = user.title,
                        firebaseUser = user.firebaseUser,

                        vm_region = potential_server_shard.vm_region,
                        vm_zone = potential_server_shard.vm_zone,

                        inParty = True,
                        partySize = team_size
                    )

                    return shard_server


        ## otherwise find the next shard with room below the transfer threshold
        logging.info('there were no previously used shards that had room')

        ## get the list of previously created shards
        previously_created_shards = serverShardController.get_list_by_serverShardTemplateKeyId(server.key.id())
        for previously_created_shard in previously_created_shards:
            logging.info('checking server shard - from prviously created ')

            ## first check from shards that are currently online
            if previously_created_shard.online:
                logging.info('checking server shard - online')
                ## if there is room, select this shard
                if previously_created_shard.playerCount + team_size <= server.sharded_player_capacity_threshold:
                    logging.info('there seems to be room on this shard')

                    ## also check placeholders

                    existing_placeholders = serverShardPlaceholderController.get_serverAssigned_by_serverShardKeyId(previously_created_shard.serverShardKeyId)

                    if previously_created_shard.playerCount + team_size + len(existing_placeholders) <= server.sharded_player_capacity_threshold:
                        logging.info('there seems to be enough room after checking placeholders')

                        shard_server = serverController.get_by_key_id(previously_created_shard.serverShardKeyId)

                        ## set up a placeholder here
                        new_placeholder = serverShardPlaceholderController.create(
                            gameKeyId = server.gameKeyId,
                            gameTitle = server.gameTitle,
                            serverClusterKeyId = server.serverClusterKeyId,
                            serverShardTemplateKeyId = server.key.id(), ## parent
                            serverShardTemplateTitle = server.title,

                            serverShardKeyId = previously_created_shard.key.id(), ## shard
                            serverShardTitle = previously_created_shard.serverShardTitle,
                            serverAssigned = True,

                            serverKeyId = shard_server.key.id(),

                            userKeyId = user.key.id(),
                            userTitle = user.title,
                            firebaseUser = user.firebaseUser,


                            #vm_region = previously_created_shard.vm_region,
                            #vm_zone = previously_created_shard.vm_zone,

                            inParty = True,
                            partySize = team_size
                        )

                        return shard_server

        ## didn't find one that was online....
        for previously_created_shard in previously_created_shards:
            logging.info('checking server shard - from prviously created - all')
            if previously_created_shard.playerCount + team_size <= server.sharded_player_capacity_threshold:
                logging.info('there seems to be room on this shard')

                ## also check placeholders

                existing_placeholders = serverShardPlaceholderController.get_serverAssigned_by_serverShardKeyId(previously_created_shard.serverShardKeyId)

                if previously_created_shard.playerCount + team_size + len(existing_placeholders) <= server.sharded_player_capacity_threshold:
                    logging.info('there seems to be enough room after checking placeholders')


                    shard_server = serverController.get_by_key_id(previously_created_shard.serverShardKeyId)

                    ## set up a placeholder here
                    new_placeholder = serverShardPlaceholderController.create(
                        gameKeyId = server.gameKeyId,
                        gameTitle = server.gameTitle,
                        serverClusterKeyId = server.serverClusterKeyId,
                        serverShardTemplateKeyId = server.key.id(), ## parent
                        serverShardTemplateTitle = server.title,

                        serverShardKeyId = previously_created_shard.key.id(), ## shard
                        serverShardTitle = previously_created_shard.serverShardTitle,
                        serverAssigned = True,

                        serverKeyId = shard_server.key.id(),

                        userKeyId = user.key.id(),
                        userTitle = user.title,
                        firebaseUser = user.firebaseUser,


                        #vm_region = previously_created_shard.vm_region,
                        #vm_zone = previously_created_shard.vm_zone,

                        inParty = True,
                        partySize = team_size
                    )

                    return shard_server


        logging.info('couldnt find a shard that can handle this many players')

        ## Instead of creating a new shard here, we just make an unassigned placeholder to let the task find it.

        ## set up a placeholder here
        new_placeholder = serverShardPlaceholderController.create(
            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,
            serverClusterKeyId = server.serverClusterKeyId,
            serverShardTemplateKeyId = server.key.id(), ## parent
            serverShardTemplateTitle = server.title,

            #serverShardKeyId = shard_server.key.id(), ## shard
            #serverShardTitle = shard_server.title,
            serverAssigned = False,

            userKeyId = user.key.id(),
            userTitle = user.title,
            firebaseUser = user.firebaseUser,


            vm_region = server.continuous_server_region,
            vm_zone = server.continuous_server_zone,

            inParty = True,
            partySize = team_size
        )

        """
        ## is there room to make another shard?
        if server.shard_count_maximum <= len(previously_created_shards):
            logging.info('no more shards are permitted. ')

            ## TODO send an error to the game discord
            return None

        shard_identifier = len(previously_created_shards) + 1
        shard_title = "%s - %s" %(server.title, shard_identifier)
        ## create a new server based on the template
        new_server_shard = serverController.create(
            title = shard_title,
            description = server.description,
            hostConnectionLink = "",
            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,
            admissionFee = server.admissionFee,
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
            maxActiveUsers = server.maxActiveUsers,
            maxAuthorizedUsers = server.maxAuthorizedUsers,
            userKeyId = server.userKeyId,
            minimumCurrencyHold = server.minimumCurrencyHold,
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
            serverClusterKeyId = server.serverClusterKeyId,
            gameLevelKeyId = server.gameLevelKeyId,
            gameLevelTitle = server.gameLevelTitle,

            vendors_allowed = server.vendors_allowed,
            player_created_vendors_allowed = server.player_created_vendors_allowed,

            ## SHARDED SERVER SPECIFICS
            sharded_server_template = False,
            sharded_from_template = True,
            sharded_from_template_serverKeyId = server.key.id(),
            sharded_from_template_serverTitle = server.title,

            #instanced_for_groupKeyId = ndb.StringProperty(indexed=True)
            #instanced_for_groupTitle = ndb.StringProperty(indexed=False)
            server_to_game_transfer_threshold = server.server_to_game_transfer_threshold,
            server_to_game_transfer_exceeded = server.server_to_game_transfer_exceeded,

            ## Custom server configuration settings, whioch can be changed inside the server itself
            configuration = server.configuration,

            drop_items_permitted = server.drop_items_permitted,
            pickup_items_permitted = server.pickup_items_permitted,

            # require badge tags to play on this server
            requireBadgeTags = server.requireBadgeTags

        )

        server_shard_record = serverShardController.create(
            serverShardTemplateKeyId = server.key.id(),
            serverShardTemplateTitle = server.title,

            serverShardKeyId = new_server_shard.key.id(),
            serverShardTitle = new_server_shard.title,

            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,

            serverClusterKeyId = server.serverClusterKeyId,
            #serverClusterTitle = ndb.StringProperty(indexed=False)

            playerCount = 0,
            playerCapacityThreshold = server.sharded_player_capacity_threshold,
            playerCapacityMaximum = server.sharded_player_capacity_maximum,

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

        ## any other housekeeping to do?

        return new_server_shard

        """
        logging.info('Placeholder set up.')
        return None



    logging.info('Not a sharded server')
    return None
