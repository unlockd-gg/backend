import logging
import datetime
import json
import random
import uuid
from google.appengine.api import taskqueue
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.servers import ServersController
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

def detect_init_parallel_server(server, user, team, team_member, group):
    logging.info('detect_init_parallel_server')

    if server.instance_server_template:
        logging.info('Found a instance_server_template')
        if server.instance_server_configuration == 'user':
            logging.info('configured for USER')
            ## check for an existing server that has already been instanciated.
            existing_instance_server = serverController.get_by_gameKeyId_serverClusterKeyId_instanced_for_userKeyId(server.gameKeyId, server.serverClusterKeyId, user.key.id())
            if existing_instance_server:
                logging.info('found existing instance')
                ## TODO update VM information in case it has changed.
                return existing_instance_server
            else:
                logging.info('no existing instance found')

                ## create a new server based on the template, and assign it to this user
                new_server_instance = serverController.create(
                    title = server.title,
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
                    invisible = True,
                    invisible_developer_setting = True,
                    continuous_server = True,
                    continuous_server_creating = False,
                    continuous_server_provisioned = False,
                    continuous_server_active = False,
                    continuous_server_entry = server.continuous_server_entry,
                    serverClusterKeyId = server.serverClusterKeyId,
                    gameLevelKeyId = server.gameLevelKeyId,
                    gameLevelTitle = server.gameLevelTitle,
                    instance_server_template = False,
                    instance_server_purge_after_use = server.instance_server_purge_after_use,
                    instance_server_purge_delay_seconds = server.instance_server_purge_delay_seconds,
                    instance_server_purge_scheduled_timestamp = server.instance_server_purge_scheduled_timestamp,
                    instance_server_configuration = server.instance_server_configuration,
                    instance_party_size_maximum = server.instance_party_size_maximum,
                    instanced_from_template = True,
                    instanced_from_template_serverKeyId = server.key.id(),
                    instanced_from_template_serverTitle = server.title,
                    instanced_server_completed = False,
                    instanced_for_userKeyId = user.key.id(),
                    instanced_for_userTitle = user.title,
                    #instanced_for_partyKeyId = ndb.StringProperty(indexed=True)
                    #instanced_for_partyTitle = ndb.StringProperty(indexed=False)
                    #instanced_for_groupKeyId = ndb.StringProperty(indexed=True)
                    #instanced_for_groupTitle = ndb.StringProperty(indexed=False)
                    server_to_game_transfer_threshold = server.server_to_game_transfer_threshold,
                    server_to_game_transfer_exceeded = server.server_to_game_transfer_exceeded,

                    vendors_allowed = server.vendors_allowed,
                    player_created_vendors_allowed = server.player_created_vendors_allowed,

                    configuration = server.configuration,

                    drop_items_permitted = server.drop_items_permitted,
                    pickup_items_permitted = server.pickup_items_permitted,

                )

                ## servers for individual users don't need a chat channel - skipping

                return new_server_instance


        elif server.instance_server_configuration == 'party':
            logging.info('configured for PARTY')

            ## If no team was found, create one
            if not team:
                title = user.title + "'s Team"

                team = teamController.create(
                    title = title,
                    description = "created via party instance join",
                    pug = True,
                    #teamAvatarTheme = player.avatar_theme,

                    gameKeyId = server.gameKeyId,
                    gameTitle = server.gameTitle,

                    #groupMembersOnly = False, ## TODO implement this?
                    #groupKey = request
                    #groupTitle = ndb.StringProperty()

                    captainPlayerKeyId = user.key.id(),
                    captainPlayerTitle = user.title,

                    teamSizeMax = server.instance_party_size_maximum,
                    teamSizeCurrent = 1,
                    teamFull = False,

                    ## State flags
                    initialized = False,
                    recruiting = True,
                    inTournament = False,
                    activeInTournament = False,
                    inMatch = False,
                    purged = False,
                )

                ## Add the captain team player record

                ## get the game player
                user_game_player = gamePlayerController.get_by_gameKeyId_userKeyId(server.gameKeyId, user.key.id())

                team_member = teamMembersController.create(
                    teamKeyId = team.key.id(),
                    teamTitle = team.title,
                    userKeyId = user.key.id(),
                    userTitle = user.title,
                    userFirebaseUser = user.firebaseUser,
                    gameKeyId = server.gameKeyId,
                    gameTitle = server.gameTitle,
                    gamePlayerKeyId = user_game_player.key.id(),
                    #playerAvatarTheme = player.avatar_theme,
                    invited = False,
                    joined = True, ## TODO double check that the user should join upon create
                    applicant = False,
                    approved = True,
                    captain = True,
                    denied = False,

                    order = 1,
                )

                ## Create the team chat channel, and subscribe the captain to it.
                party_chat_title = "party chat"
                party_chat_channel = chatChannelController.create(
                    title = party_chat_title,
                    channel_type = 'team',
                    #adminUserKeyId = user.key.id(),
                    refKeyId = team.key.id(),
                    gameKeyId = server.gameKeyId,
                    max_subscribers = 20
                )

                subscriber = chatChannelSubscribersController.create(
                    online = True,
                    chatChannelKeyId = party_chat_channel.key.id(),
                    chatChannelTitle = party_chat_channel.title,
                    userKeyId = user.key.id(),
                    userTitle = user.title,
                    userFirebaseUser = user.firebaseUser,
                    post_count = 0,
                    chatChannelRefKeyId = team.key.id(),
                    channel_type = 'team',
                    #chatChannelOwnerKeyId = user.key.id()
                )

                chat_message = "> Joined party chat"

                ## push the chat channel list and a chat message

                taskUrl='/task/chat/channel/list_changed'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                'userKeyId': user.key.id(),
                                                                                'textMessage': chat_message
                                                                                }, countdown = 2)

                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": chat_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })

                ## queue up the task to send a message to all team members
                taskUrl='/task/team/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)



            ## check for an existing server that has already been instanciated.
            existing_instance_server = serverController.get_by_gameKeyId_serverClusterKeyId_instanced_for_partyKeyId(server.gameKeyId, server.serverClusterKeyId, team.key.id())
            if existing_instance_server:
                logging.info('found existing instance')
                ## TODO update VM information in case it has changed.
                return existing_instance_server
            else:
                logging.info('no existing instance found')

                ## make sure the player is in a party/team
                if not team_member:
                    logging.info('NOT on a team - sending a chat message')

                    error_message = "You must be in a party to enter this instance"
                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                        "message": error_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    }, countdown = 0,)
                    return None

                ## make sure that this player is the party leader
                ## TODO think about this.  maybe we want any player to be able to start the instance?
                if not team_member.captain:
                    logging.info('NOT team captain - sending a chat message')

                    error_message = "Only the team captain can create the instance."
                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                        "message": error_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    }, countdown = 0,)
                    return None

                ## create a new server based on the template, and assign it to this team
                new_server_instance = serverController.create(
                    title = server.title,
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
                    invisible = True,
                    invisible_developer_setting = True,
                    continuous_server = True,
                    continuous_server_creating = False,
                    continuous_server_provisioned = False,
                    continuous_server_active = False,
                    continuous_server_entry = server.continuous_server_entry,
                    serverClusterKeyId = server.serverClusterKeyId,
                    gameLevelKeyId = server.gameLevelKeyId,
                    gameLevelTitle = server.gameLevelTitle,
                    instance_server_template = False,
                    instance_server_purge_after_use = server.instance_server_purge_after_use,
                    instance_server_purge_delay_seconds = server.instance_server_purge_delay_seconds,
                    instance_server_purge_scheduled_timestamp = server.instance_server_purge_scheduled_timestamp,
                    instance_server_configuration = server.instance_server_configuration,
                    instance_party_size_maximum = server.instance_party_size_maximum,
                    instanced_from_template = True,
                    instanced_from_template_serverKeyId = server.key.id(),
                    instanced_from_template_serverTitle = server.title,
                    instanced_server_completed = False,
                    #instanced_for_userKeyId = user.key.id(),
                    #instanced_for_userTitle = user.title,
                    instanced_for_partyKeyId = team.key.id(),
                    instanced_for_partyTitle = team.title,
                    #instanced_for_groupKeyId = ndb.StringProperty(indexed=True)
                    #instanced_for_groupTitle = ndb.StringProperty(indexed=False)
                    server_to_game_transfer_threshold = server.server_to_game_transfer_threshold,
                    server_to_game_transfer_exceeded = server.server_to_game_transfer_exceeded,

                    vendors_allowed = server.vendors_allowed,
                    player_created_vendors_allowed = server.player_created_vendors_allowed,

                    configuration = server.configuration,

                    drop_items_permitted = server.drop_items_permitted,
                    pickup_items_permitted = server.pickup_items_permitted,

                )

                ## servers for parties don't need a chat channel - skipping

                return new_server_instance

        elif server.instance_server_configuration == 'group':
            logging.info('configured for GROUP')

            if not group:
                logging.info('NOT in a group - sending a chat message')

                error_message = "You must be in a group to enter this instance"
                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": error_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                }, countdown = 0,)
                return None

            ## make sure the group member exists
            group_user = groupUserController.get_by_groupKeyId_userKeyId(group.key.id(), user.key.id())
            if not group_user:
                logging.info('Group not found - sending a chat message')

                error_message = "Group not found"
                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": error_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                }, countdown = 0,)
                return None

            ## make sure the group member has the join instance permission
            group_role = groupRoleController.get_by_key_id(group_user.roleKeyId)
            if not group_role:
                logging.info('Group role not found - sending a chat message')

                error_message = "Group role not found"
                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": error_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                }, countdown = 0,)
                return None

            if not group_role.join_group_server_instances:
                logging.info('Group role does not have join_group_server_instances permission')

                error_message = "You don't have permission to join this group's instances"
                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": error_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                }, countdown = 0,)
                return None

            ## make sure the group is connected to this game
            group_game = groupGameController.get_by_groupKeyId_gameKeyId(group.key.id(), server.gameKeyId)
            if not group_game:
                logging.info('Group game not found')

                error_message = "The group is not connected to this game."
                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    "message": error_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                }, countdown = 0,)
                return None


            ## check for an existing server that has already been instanciated.
            existing_instance_server = serverController.get_by_gameKeyId_serverClusterKeyId_instanced_for_groupKeyId(server.gameKeyId, server.serverClusterKeyId, group.key.id())
            if existing_instance_server:
                logging.info('found existing instance')
                ## TODO update VM information in case it has changed.
                return existing_instance_server
            else:
                logging.info('no existing instance found')

                ## create a new server based on the template, and assign it to this group
                new_server_instance = serverController.create(
                    title = server.title,
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
                    invisible = True,
                    invisible_developer_setting = True,
                    continuous_server = True,
                    continuous_server_creating = False,
                    continuous_server_provisioned = False,
                    continuous_server_active = False,
                    continuous_server_entry = server.continuous_server_entry,
                    serverClusterKeyId = server.serverClusterKeyId,
                    gameLevelKeyId = server.gameLevelKeyId,
                    gameLevelTitle = server.gameLevelTitle,
                    instance_server_template = False,
                    instance_server_purge_after_use = server.instance_server_purge_after_use,
                    instance_server_purge_delay_seconds = server.instance_server_purge_delay_seconds,
                    instance_server_purge_scheduled_timestamp = server.instance_server_purge_scheduled_timestamp,
                    instance_server_configuration = server.instance_server_configuration,
                    instance_party_size_maximum = server.instance_party_size_maximum,
                    instanced_from_template = True,
                    instanced_from_template_serverKeyId = server.key.id(),
                    instanced_from_template_serverTitle = server.title,
                    instanced_server_completed = False,
                    #instanced_for_userKeyId = user.key.id(),
                    #instanced_for_userTitle = user.title,
                    #instanced_for_partyKeyId = team.key.id(),
                    #instanced_for_partyTitle = team.title,
                    instanced_for_groupKeyId = group.key.id(),
                    instanced_for_groupTitle = group.title,
                    server_to_game_transfer_threshold = server.server_to_game_transfer_threshold,
                    server_to_game_transfer_exceeded = server.server_to_game_transfer_exceeded,

                    vendors_allowed = server.vendors_allowed,
                    player_created_vendors_allowed = server.player_created_vendors_allowed,

                    configuration = server.configuration,

                    drop_items_permitted = server.drop_items_permitted,
                    pickup_items_permitted = server.pickup_items_permitted,

                )

                ## servers for parties don't need a chat channel - skipping

                return new_server_instance



        else:
            logging.error('configured for none')

    logging.info('Not a parallel server')
    return server
