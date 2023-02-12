import logging
import datetime
import string
import json
import random

import google.oauth2.id_token
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from httplib2 import Http
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController

from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.game_levels import GameLevelsController
from apps.uetopia.controllers.game_level_links import GameLevelLinksController
#from apps.uetopia.controllers.sense import SenseController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_users import GroupUsersController

#from apps.uetopia.utilities.server_player_deactivate import deactivate_player
from apps.uetopia.utilities.weighted_choice import weighted_choice

from apps.uetopia.utilities.server_parallel_template_detect_init import detect_init_parallel_server
from apps.uetopia.utilities.server_shard_detect_init import detect_init_shard_server

from configuration import *

requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class TransferPlayerHandler(BaseHandler):
    def post(self, targetServerKeyId, userid):
        """
        Transfer a player from one server to another
        Requires http headers:  Key, Sign
        Requires POST parameters:  userid, target_server_key, nonce
        Optional POST parameters: checkOnly
        """

        ## Deactivate The player on the authenticated server
        ## Move balance/rank on server player
        ## unlock and save game player
        ## Activate the player on the target server

        ## Handle infinite server creation mode


        gameController = GamesController()
        serverController = ServersController()
        usersController = UsersController()
        spController = ServerPlayersController()
        gpController = GamePlayersController()
        gameCharactersController = GameCharactersController()
        serverLinksController = ServerLinksController()
        serverClusterController = ServerClustersController()
        gameLevelController = GameLevelsController()
        gameLevelLinkController = GameLevelLinksController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()

        teamController = TeamsController()
        teamMemberController = TeamMembersController()
        groupsController = GroupsController()

        serverShardController = ServerShardsController()
        serverShardPlaceholderController = ServerShardPlaceholderController()


        ## the server is the UE server that is making the request.
        ## the player is currently here.
        server = serverController.verify_signed_auth(self.request)
        default_currency_display = None
        default_currency_conversion = None
        toShard = False # hang on to this for return values


        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                success = False,
                checkOnly = checkonly,
                toShard = toShard
            )
        else:
            logging.info('auth success')

            ## First update the player list with all of the pending authorizations and deauthorizations.

            incoming_userid = userid #self.request.POST.get('userid', None)
            player_userid = incoming_userid

            logging.info("incoming_userid: %s" % incoming_userid)
            logging.info("serverKeyId: %s" % server.key.id())

            ## checkOnly is used so that servers can test if players are permitted to travel without activating the transfer
            checkonly = self.request.get('checkOnly', 'false')
            logging.info("checkonly: %s" % checkonly)

            ## toShard is used to inform the backend that it is just a shard trnasfer, not a full travel
            toShard = self.request.get('toShard', 'false')
            logging.info("toShard: %s" % toShard)

            ## the target server is the server that this server link is pointing to.
            target_server = serverController.get_by_key_id(int(targetServerKeyId))
            if not target_server:
                logging.info('target server could not be found')
                return self.render_json_response(
                    authorization = True,
                    error = "The target server could not be found.",
                    success = False,
                    checkOnly = checkonly,
                    toShard = toShard
                )

            ## get the game
            game = gameController.get_by_key_id(server.gameKeyId)
            if not game:
                return self.render_json_response(
                    authorization = True,
                    error = "The game could not be found.",
                    success = False,
                    checkOnly = checkonly,
                    toShard = toShard
                )

            if not player_userid:
                logging.info('userid not found in post')
                return self.render_json_response(
                    authorization = True,
                    error = "userid not found in post.",
                    success = False,
                    checkOnly = checkonly,
                    toShard = toShard
                )

            player = usersController.get_by_key_id(int(incoming_userid))

            if not player:
                logging.info('user not found using userID')
                return self.render_json_response(
                    authorization = True,
                    error = "user not found using userID.",
                    success = False,
                    checkOnly = checkonly,
                    toShard = toShard
                )

            # get the game player
            game_player = gpController.get_by_gameKeyId_userKeyId(game.key.id(), int(incoming_userid))
            if not game_player:
                logging.error('game player not found!')

            ## make sure the game player has the required tags
            if target_server.requireBadgeTags:
                player_has_all_tags = True
                missing_tags = []
                missingTagsTextMessage = "> You do not have the tags required to join this server.  You are missing: "
                for tag in target_server.requireBadgeTags:
                    if not game_player.badgeTags:
                        missing_tags.append(tag)
                        missingTagsTextMessage = missingTagsTextMessage + tag + ", "
                        player_has_all_tags = False
                        continue
                    if tag not in game_player.badgeTags:
                        missing_tags.append(tag)
                        missingTagsTextMessage = missingTagsTextMessage + tag + ", "
                        player_has_all_tags = False
                        continue

                if not player_has_all_tags:
                    logging.info('player is missing a required tag')

                    missingTagsTextMessage = missingTagsTextMessage + ".  Check the available game offers to acquire these tags."

                    chat_msg = json.dumps({"type":"chat",
                                            "textMessage":missingTagsTextMessage,
                                            "userKeyId": "SYSTEM",
                                            "userTitle": "SYSTEM",
                                            #"chatMessageKeyId": chatMessageKeyId,
                                            #"chatChannelTitle": channel.title,
                                            #"chatChannelKeyId": channel.key.id(),
                                            "created":datetime.datetime.now().isoformat()
                    })

                    # push out to in-game clients via heroku
                    # ignore if it's failing
                    try:
                        URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, user.firebaseUser)
                        resp, content = http_auth.request(URL,
                                            ##"PATCH",
                                          "PUT", ## Write or replace data to a defined path,
                                          chat_msg,
                                          headers=headers)

                        logging.info(resp)
                        logging.info(content)
                    except:
                        logging.error('heroku error')

            ## DO shard transfer logic


            ## shard to shard is easy so long as they match
            if server.sharded_from_template and target_server.sharded_from_template:
                logging.info('both servers are sharded')
                if server.sharded_from_template_serverKeyId == target_server.sharded_from_template_serverKeyId:
                    logging.info('both servers share the same shard template')
                    toShard = True
                    if target_server.continuous_server_provisioned:
                        logging.info('sharded target is provisioned')

                        ## shard to shard travel does not use links.  Set this to none so it does not get added later.
                        target_server_link = None
                    else:
                        logging.info('sharded target is not provisioned')

                        ## send a text chat to the user that initiated the request
                        chat_message = "Bringing up shard, stand by. "
                        taskUrl='/task/chat/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': player.firebaseUser,
                                                                                            "message": chat_message,
                                                                                            "created":datetime.datetime.now().isoformat()
                                                                                        })
                        logging.info('Starting VM allocate task')
                        ## start a task to create the vm
                        taskUrl='/task/server/vm/allocate'
                        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                "serverKeyId": target_server.key.id()
                                                                                            })
                        return self.render_json_response(
                            authorization = True,
                            error = "Starting up server shard.",
                            success = False,
                            checkOnly = checkonly,
                            toShard = toShard
                        )
                else:
                    logging.error('server shards do not share the same template - this should not be possible.')
                    return self.render_json_response(
                        authorization = True,
                        error = "server shards do not share the same template.",
                        success = False,
                        checkOnly = checkonly,
                        toShard = toShard
                    )
            else:


                ## get the server link - instanced servers should use the parent key
                if server.instanced_from_template:
                    target_server_link = serverLinksController.get_by_originServerKeyId_targetServerKeyId(server.instanced_from_template_serverKeyId, target_server.key.id())
                ## same for sharded servers
                elif server.sharded_from_template:
                    target_server_link = serverLinksController.get_by_originServerKeyId_targetServerKeyId(server.sharded_from_template_serverKeyId, target_server.key.id())
                else:
                    target_server_link = serverLinksController.get_by_originServerKeyId_targetServerKeyId(server.key.id(), target_server.key.id())

                if not target_server_link:
                    logging.info('server link could not be found')
                    return self.render_json_response(
                        authorization = True,
                        error = "The server link could not be found.",
                        success = False,
                        checkOnly = checkonly,
                        toShard = toShard
                    )

                ## get server cluster
                server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)
                if not server_cluster:
                    return self.render_json_response(
                        authorization = True,
                        error = "The server cluster could not be found.",
                        success = False,
                        checkOnly = checkonly,
                        toShard = toShard
                    )

                if not target_server_link.permissionCanUserTravel:
                    return self.render_json_response(
                        authorization = True,
                        error = "permissionCanUserTravel is set to False.",
                        success = False,
                        checkOnly = checkonly,
                        toShard = toShard
                    )



                ## Before actually running the player logic, handle infinite server mode
                if server_cluster.serverCreationMode == 'infinite':
                    logging.info('serverCreationMode: infinite')

                    if target_server.infinite_server_unused:
                        logging.info('infinite_server_unused: True')

                        ## we need to setup all of this server's links, and any linked servers
                        # get the game level that this server is referencing
                        target_server_game_level = gameLevelController.get_by_key_id(target_server.gameLevelKeyId)
                        if not target_server_game_level:
                            logging.error('server game level not found')
                            return self.render_json_response(
                                authorization = True,
                                error = "server game level not found.",
                                success = False,
                                checkOnly = checkonly,
                                toShard = toShard
                            )


                        ## pick a random number of links between the min and max
                        serverlink_spawn_count = random.randint(target_server_game_level.outgoingLinkMin, target_server_game_level.outgoingLinkMax)

                        ## does the game even have enough CRED to transfer over here to get it going?
                        if game.currencyBalance < server_cluster.game_to_server_initial_transfer_amount * (serverlink_spawn_count +2):
                            logging.info("The game does not have enough CRED to spin up this server.")

                            ## do slack/discord pushes if enabled
                            if game.slack_subscribe_errors and game.slack_webhook:
                                http_auth = Http()
                                headers = {"Content-Type": "application/json"}
                                message = "Error: The game does not have enough currency balance to create new servers"
                                slack_data = {'text': message}
                                data=json.dumps(slack_data)
                                resp, content = http_auth.request(game.slack_webhook,
                                                  "POST",
                                                  data,
                                                  headers=headers)

                            if game.discord_subscribe_errors and game.discord_webhook_admin:
                                http_auth = Http()
                                headers = {"Content-Type": "application/json"}
                                message = "Error: The game does not have enough currency balance to create new servers"
                                url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                                discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                                data=json.dumps(discord_data)
                                resp, content = http_auth.request(game.discord_webhook_admin,
                                                  "POST",
                                                  data,
                                                  headers=headers)


                            return self.render_json_response(
                                authorization = True,
                                error = "The game does not have enough CRED to spin up this server.",
                                success = False,
                                checkOnly = checkonly,
                                toShard = toShard
                            )

                        # get the game level links
                        logging.info('target_server.gameLevelKeyId: %s'%target_server.gameLevelKeyId)
                        gameLinkList = gameLevelLinkController.list_by_gameLevelKeyId_not_return(target_server.gameLevelKeyId)
                        logging.info('len(gameLinkList): %s'% len(gameLinkList))
                        allGameLinks = gameLinkList

                        ## do return link first
                        returnlink_roll = random.random()
                        if returnlink_roll < target_server_game_level.chanceToCreateReturnLink:
                            logging.info('creating return link')

                            return_gameLink = gameLevelLinkController.get_returnLink_by_gameLevelKeyId(target_server.gameLevelKeyId)

                            serverLink = serverLinksController.create(
                                originServerKeyId = target_server.key.id(),
                                originServerTitle = target_server.title,
                                serverClusterKeyId = server_cluster.key.id(),
                                serverClusterTitle = server_cluster.title,
                                targetServerKeyId = server.key.id(),
                                targetServerTitle = server.title,
                                targetStatusIsContinuous = server.continuous_server,
                                targetStatusProvisioned = server.continuous_server_provisioned,
                                targetStatusOnline = server.continuous_server_active,
                                targetStatusCreating = server.continuous_server_creating,
                                targetStatusFull = False, ## TODO
                                targetStatusDead = False, ## TODO
                                permissionCanMount = True,
                                permissionCanUserTravel = True,
                                permissionCanDismount = False,
                                isEntryPoint = False,
                                userKeyId = game.userKeyId,
                                resourcesUsedToTravel = return_gameLink.resourcesUsedToTravel,
                                resourceAmountsUsedToTravel = return_gameLink.resourceAmountsUsedToTravel,
                                currencyCostToTravel = return_gameLink.currencyCostToTravel,
                                coordLocationX = return_gameLink.locationX,
                                coordLocationY = return_gameLink.locationY,
                                coordLocationZ = return_gameLink.locationZ,
                                gameKeyId = game.key.id()
                            )

                        ## random chance link next
                        randomlink_roll = random.random()
                        if randomlink_roll < target_server_game_level.chanceToCreateRandomLink:
                            logging.info('creating random link to an existing server.')

                            picked_gameLevelLink, index = weighted_choice(gameLinkList)
                            ## remove the picked link from the list
                            del gameLinkList[index]

                            random_server_link_choice_list = serverLinksController.get_list_by_originServerKeyId(server.key.id())
                            ## remove the link we just followed
                            for i, random_server_link_choice in enumerate(random_server_link_choice_list):
                                if random_server_link_choice.targetServerKeyId == target_server.key.id():
                                    del random_server_link_choice_list[i]
                                    break
                            ## TODO modularize this, for now just doing one level
                            picked_server_link_choice = random.choice(random_server_link_choice_list)
                            picked_server = serverController.get_by_key_id(picked_server_link_choice.targetServerKeyId)

                            ## create the link to the picked server
                            serverLink = serverLinksController.create(
                                originServerKeyId = target_server.key.id(),
                                originServerTitle = target_server.title,
                                serverClusterKeyId = server_cluster.key.id(),
                                serverClusterTitle = server_cluster.title,
                                targetServerKeyId = picked_server.key.id(),
                                targetServerTitle = picked_server.title,
                                targetStatusIsContinuous = picked_server.continuous_server,
                                targetStatusProvisioned = picked_server.continuous_server_provisioned,
                                targetStatusOnline = picked_server.continuous_server_active,
                                targetStatusCreating = picked_server.continuous_server_creating,
                                targetStatusFull = False, ## TODO
                                targetStatusDead = False, ## TODO
                                permissionCanMount = True,
                                permissionCanUserTravel = True,
                                permissionCanDismount = False,
                                isEntryPoint = False,
                                userKeyId = game.userKeyId,
                                resourcesUsedToTravel = picked_gameLevelLink.resourcesUsedToTravel,
                                resourceAmountsUsedToTravel = picked_gameLevelLink.resourceAmountsUsedToTravel,
                                currencyCostToTravel = picked_gameLevelLink.currencyCostToTravel,
                                coordLocationX = picked_gameLevelLink.locationX,
                                coordLocationY = picked_gameLevelLink.locationY,
                                coordLocationZ = picked_gameLevelLink.locationZ,
                                gameKeyId = game.key.id()
                            )

                        if serverlink_spawn_count >0:
                            # get all the possible game Levels
                            gameLevelList = gameLevelController.list_by_gameKeyId(target_server.gameKeyId)

                            if len(gameLinkList) >= serverlink_spawn_count:

                                ## go through the servers that we need to spawn, and pick links by probability.
                                for i in range(serverlink_spawn_count):
                                    picked_gameLevelLink, index = weighted_choice(gameLinkList)
                                    ## remove the picked link from the list
                                    del gameLinkList[index]

                                    ## pick a game level by probability for each server.
                                    picked_gameLevel, index = weighted_choice(gameLevelList)

                                    ## set up the server
                                    target_new_server = serverController.create(
                                        title = picked_gameLevel.title,
                                        #description = request.description,
                                        hostAddress = "1",
                                        hostPort = "1",
                                        hostConnectionLink = "1",
                                        gameKeyId = game.key.id(),
                                        gameTitle = game.title,
                                        userKeyId = game.userKeyId,
                                        minimumCurrencyHold = picked_gameLevel.minimumCurrencyHold,
                                        totalCurrencyHeld = 0,
                                        #incrementCurrency = SERVER_CREATE_DEFAULT_INCREMENTCURRENCY,
                                        currencyAwarded = 0,
                                        apiKey = serverController.create_unique_api_key(),
                                        apiSecret = serverController.key_generator(),
                                        continuous_server = True,
                                        continuous_server_provisioned = False,
                                        continuous_server_entry = False,
                                        continuous_server_creating = False,
                                        continuous_server_active = False,

                                        ## moved to server cluster
                                        #continuous_server_project = server.continuous_server_project,
                                        #continuous_server_bucket = server.continuous_server_bucket,
                                        #continuous_server_region = server.continuous_server_region,
                                        #continuous_server_zone = server.continuous_server_zone,
                                        #continuous_server_source_disk_image = server.continuous_server_source_disk_image,
                                        #continuous_server_machine_type = server.continuous_server_machine_type,
                                        #continuous_server_startup_script_location = server.continuous_server_startup_script_location,
                                        #continuous_server_shutdown_script_location = server.continuous_server_shutdown_script_location,

                                        ## SHARDED SERVER SPECIFICS
                                        sharded_server_template = picked_gameLevel.sharded_server_template,
                                        shard_count_maximum = picked_gameLevel.shard_count_maximum,
                                        sharded_player_capacity_threshold = picked_gameLevel.sharded_player_capacity_threshold,
                                        sharded_player_capacity_maximum = picked_gameLevel.sharded_player_capacity_maximum,

                                        serverInfoRefreshNeeded = False,
                                        invisible = False,
                                        invisible_developer_setting = False,
                                        admissionFee = 10000,
                                        serverClusterKeyId = server_cluster.key.id(),
                                        session_host_address = "1",
                                        session_id = "1",

                                        infinite_server_unused = True,
                                        gameLevelKeyId = picked_gameLevel.key.id(),
                                        gameLevelTitle =picked_gameLevel.title,

                                        server_to_game_transfer_threshold = server_cluster.server_to_game_transfer_threshold,
                                        travelMode = server_cluster.travelMode,
                                        randomRef = random.random(),
                                        #serverCurrency = server_cluster.game_to_server_initial_transfer_amount
                                    )

                                    ## transactions disbled for servers
                                    """
                                    server_create_transaction = transactionController.create(
                                        amountInt = server_cluster.game_to_server_initial_transfer_amount,
                                        description = "Game to Server transfer",
                                        serverKeyId = target_new_server.key.id(),
                                        serverTitle = target_new_server.title,
                                        transactionType = "server",
                                        transactionClass = "creation transfer",
                                        transactionSender = False,
                                        transactionRecipient = True,
                                        submitted = True,
                                        processed = True, # marked as processed because it is already applied.
                                        materialIcon = MATERIAL_ICON_SERVER_CREATE,
                                        materialDisplayClass = "md-primary"
                                    )

                                    description = "Server Startup transfer to: %s" %target_new_server.key.id()
                                    recipient_transaction = transactionController.create(
                                        amountInt = -server_cluster.game_to_server_initial_transfer_amount,
                                        ##amount = ndb.FloatProperty(indexed=False) # for display
                                        ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                                        ##newBalance = ndb.FloatProperty(indexed=False) # for display
                                        description = description,
                                        ##userKeyId = authorized_user.key.id(),
                                        ##firebaseUser = authorized_user.firebaseUser,
                                        ##targetUserKeyId = ndb.IntegerProperty()
                                        gameKeyId = game.key.id(),
                                        gameTitle = game.title,

                                        ##  transactions are batched and processed all at once.
                                        transactionType = "game",
                                        transactionClass = "server creation transfer",
                                        transactionSender = True,
                                        transactionRecipient = False,
                                        submitted = True,
                                        processed = False,
                                        materialIcon = MATERIAL_ICON_SERVER_CREATE,
                                        materialDisplayClass = "md-accent"
                                    )

                                    ## only start pushable tasks.  If they are not pushable, there is already a task running.
                                    pushable = lockController.pushable("game:%s"%game.key.id())
                                    if pushable:
                                        logging.info('game pushable')
                                        taskUrl='/task/game/transaction/process'
                                        taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                                                "key_id": game.key.id()
                                                                                                            }, countdown=2)


                                    """

                                    ## Set up the server link
                                    serverLink = serverLinksController.create(
                                        originServerKeyId = target_server.key.id(),
                                        originServerTitle = target_server.title,
                                        serverClusterKeyId = server_cluster.key.id(),
                                        serverClusterTitle = server_cluster.title,
                                        targetServerKeyId = target_new_server.key.id(),
                                        targetServerTitle = target_new_server.title,
                                        targetStatusIsContinuous = target_new_server.continuous_server,
                                        targetStatusProvisioned = target_new_server.continuous_server_provisioned,
                                        targetStatusOnline = target_new_server.continuous_server_active,
                                        targetStatusCreating = target_new_server.continuous_server_creating,
                                        targetStatusFull = False,
                                        targetStatusDead = False,
                                        permissionCanMount = True,
                                        permissionCanUserTravel = True,
                                        permissionCanDismount = False,
                                        isEntryPoint = False,
                                        userKeyId = game.userKeyId,
                                        resourcesUsedToTravel = picked_gameLevelLink.resourcesUsedToTravel,
                                        resourceAmountsUsedToTravel = picked_gameLevelLink.resourceAmountsUsedToTravel,
                                        currencyCostToTravel = picked_gameLevelLink.currencyCostToTravel,
                                        coordLocationX = picked_gameLevelLink.locationX,
                                        coordLocationY = picked_gameLevelLink.locationY,
                                        coordLocationZ = picked_gameLevelLink.locationZ,
                                        gameKeyId = game.key.id()
                                    )

                                    ## set up the chat channel for this newly created server
                                    server_chat_title = picked_gameLevel.title + " chat"
                                    chat_channel = ChatChannelsController().create(
                                        title = server_chat_title,
                                        #text_enabled = True,
                                        #data_enabled = False,
                                        channel_type = 'server',
                                        adminUserKeyId = game.userKeyId,
                                        refKeyId = target_new_server.key.id(),
                                        max_subscribers = 200
                                    )


                                ## endfor

                        ## mark server as processed.
                        target_server.infinite_server_unused = False
                        serverController.update(target_server)

                    ## end infinite mode

            authorized = False



            server_to_use = target_server # set this in case instance is disabled

            ## handle sharded mode...
            ## this is different than the check above...
            ## this is checking to see if a player is travelling onto a sharded server from somewhere else.
            if target_server.sharded_server_template:
                logging.info('found a sharded server template')

                ## get the user's team/party (if any)
                team = None
                team_member = teamMemberController.get_by_gameKeyId_userKeyId(game.key.id(), int(incoming_userid))
                if team_member:
                    team = teamController.get_by_key_id(team_member.teamKeyId)

                server_to_use = detect_init_shard_server(target_server, player, team, team_member)

                ## send a message out to the player informing them of the status.
                if server_to_use:
                    if checkonly == 'false':
                        logging.info('checkonly is false')

                        chat_message = "Transferring to shard, stand by. "
                        taskUrl='/task/chat/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': player.firebaseUser,
                                                                                            "message": chat_message,
                                                                                            "created":datetime.datetime.now().isoformat()
                                                                                        })
                    else:
                        logging.info('checkonly is true')

                        chat_message = "Travel approved. "
                        taskUrl='/task/chat/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': player.firebaseUser,
                                                                                            "message": chat_message,
                                                                                            "created":datetime.datetime.now().isoformat()
                                                                                        })


                else:
                    chat_message = "Bringing up shard, stand by. "
                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': player.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })


            ## handle parallel/instanced mode

            elif target_server.instance_server_template:
                logging.info('found an instance template')

                ## get the user's team/party (if any)
                team = None
                team_member = teamMemberController.get_by_gameKeyId_userKeyId(game.key.id(), int(incoming_userid))
                if team_member:
                    team = teamController.get_by_key_id(team_member.teamKeyId)

                ## get the user's group (if any)
                group = None
                if player.groupTagKeyId:
                    group = groupsController.get_by_key_id(player.groupTagKeyId)

                ## check and handle parallel server mode
                server_to_use = detect_init_parallel_server(target_server, player, team, team_member, group)

            # first check to see if there is a server player member record for the origin server NOT server_to_use
            server_player_member = spController.get_server_user(server.key.id(), player.key.id() )

            if server_player_member:
                logging.info('server_player_member found')
                logging.info('server_player_member currencyCurrent: %s' % server_player_member.currencyCurrent)

                new_rank = self.request.get('rank', None)
                #currency_balance = server_player_member.currencyCurrent

                ## hang on to this balance to copy over to the new server player

                ## this isn't really working, so I'm disabling the currency transfer feature.
                ## all servers will auth and deauth independantly now.
                #moved_balance = currency_balance

                if checkonly == 'false':
                    logging.info('checkOnly is false - deactivating the server player')


                ## We need to store the server link in here so that the target server can spawn the player at the right location.
                ## if characters are enabled - store this value in the character.  Otherwise use game player
                ## hopefully there is enough time between transfer and save game player to not violate 1 sec rule.  testing.
                if game_player.characterCurrentKeyId:
                    logging.info('characters are enabled and one is selected.')
                    game_player_character = gameCharactersController.get_by_key_id(game_player.characterCurrentKeyId)
                    if game_player_character:
                        logging.info('found the game character')
                        ## only update if different
                        ## shard to shard travel does not use links.  skip if not set
                        if target_server_link:
                            if game_player_character.lastServerLinkKeyId != target_server_link.key.id():
                                logging.info('lastServerKeyId is different - updating')
                                game_player_character.lastServerLinkKeyId = target_server_link.key.id()  #from link
                                gameCharactersController.update(game_player_character)
                else:
                    logging.info('characters not enabled or not selected')
                    ## only update if different
                    ## shard to shard travel does not use links.  skip if not set
                    if target_server_link:
                        if game_player.lastServerLinkKeyId != target_server_link.key.id():
                            logging.info('lastServerKeyId is different - updating')
                            game_player.lastServerLinkKeyId = target_server_link.key.id()  #from link
                            gpController.update(game_player)

                    ## muting this as it's getting called twice.
                    #deactivate_player(server_player_member, new_rank, currency_balance, transfer=True)

                ## Check to see if the target server has a server player member record
                ## ?? not doing anything with this - muting
                #target_server_player_member = spController.get_server_user(server_to_use.key.id(), player.key.id() )



                ## TODO game player verify unlocked

                ## set the current server location in gameplayer

                if checkonly == 'false':
                    logging.info('checkonly is false, SKIPPING - updating game player')
                    #game_player.lastServerKeyId = target_server.key.id()
                    #game_player.locked = False


                ##  pushes and notifications

                ## VM activate
                ## make sure it exists - it could have errored out
                if server_to_use:
                    if server_to_use.continuous_server:
                        logging.info('server_to_use.continuous')
                        if not server_to_use.continuous_server_creating:
                            logging.info('server_to_use.continuous_server_creating is FALSE')
                            if not server_to_use.continuous_server_provisioned:
                                logging.info('server_to_use.continuous_server_provisioned is FALSE')
                                logging.info('Starting VM allocate task')
                                ## start a task to create the vm
                                taskUrl='/task/server/vm/allocate'
                                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                        "serverKeyId": server_to_use.key.id()
                                                                                                    })



                    logging.info('targetServerKeyId: %s' %server_to_use.key.id())

                    ## get the instance
                    return self.render_json_response(
                        authorization = True,
                        success = True,
                        targetServerKeyId = str(target_server.key.id()), # this is the key of the parent (non instanced) server.  needs to be a string otherwise UE adds a .0
                        userKeyId = incoming_userid,
                        checkOnly = checkonly,
                        ## Instanced servers need some extra handling here.
                        ## since we can't poll for them globally, we need to pass state information for the instanced server on a per-user basis.
                        ## doing that here.
                        ## TODO maybe consider moving all of the server travel stuff into the Online Subsystem
                        instanceServerTemplate = target_server.instance_server_template,
                        instanceServerKeyId = str(server_to_use.key.id()), ## this is the key of the specific instance server.
                        instanceCreating = server_to_use.continuous_server_creating,
                        instanceProvisioned = server_to_use.continuous_server_provisioned,
                        instanceOnline = server_to_use.continuous_server_online or False,
                        instanceHostConnectionLink = server_to_use.hostConnectionLink,
                        instanceSessionHostAddress = server_to_use.session_host_address,
                        instanceSessionId = server_to_use.session_id,
                        toShard = toShard
                        ## sharded servers need some extra handling here?
                        ## TODO add stuff for sharded servers
                    )

                else:
                    logging.info('server_to_use not found')

                    return self.render_json_response(
                        authorization = True,
                        error = "server_to_use not found.",
                        success = False,
                        targetServerKeyId = None,
                        userKeyId = incoming_userid,
                        checkOnly = checkonly,
                        toShard = toShard
                    )

            #taskUrl='/task/server/push'
            #taskqueue.add(url=taskUrl, queue_name='serverPush', params={'key': server.key.urlsafe()}, countdown = 2,)
