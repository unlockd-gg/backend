import logging
import json
import datetime
from apps.handlers import BaseHandler
#from google.appengine.api import users
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
#from protorpc import remote
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from httplib2 import Http
from google.appengine.api import urlfetch

from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController
from apps.uetopia.controllers.server_instances import ServerInstancesController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class OnVmCrashHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def get(self, serverKeyId, serverSecret):
        return self.post(serverKeyId, serverSecret)

    def post(self, serverKeyId, serverSecret):
        """ Static Index

        """
        logging.info('OnVmCrashHandler')

        ## Is this a server or match that crashed?
        serverController = ServersController()
        serverClusterController = ServerClustersController()
        serverPlayerController = ServerPlayersController()
        ucontroller = UsersController()
        gpController = GamePlayersController()
        gameController = GamesController()
        gameCharacterController = GameCharactersController()
        gameModeController = GameModesController()

        matchController = MatchController()
        matchPlayerController = MatchPlayersController()

        lockController = TransactionLockController()
        transactionController = TransactionsController()

        chatMessageController = ChatMessagesController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscriberController = ChatChannelSubscribersController()
        serverInstancesController = ServerInstancesController()

        serverShardController = ServerShardsController()


        server = serverController.get_by_api_key(serverKeyId)

        if server:
            logging.info('This is a server')

            ## check to see if the server has already been brought down safely.

            game = gameController.get_by_key_id(server.gameKeyId)

            if not game:
                logging.info('game not found')
                return self.render_json_response(
                    authorization = True,
                    error= "The game was not found."
                    )

            ## also get the server cluster so we can get all of the VM info
            server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)
            if not server_cluster:
                logging.info('server_cluster not found')
                return self.render_json_response(
                    authorization = True,
                    error= "The server_cluster was not found."
                    )

            ## We have a server that crashed.
            ## Get all of the server_players that are active and deactivate them
            ## get GamePlayer / GameCharacter and Unlock it.
            ## Run the deallocation task
            ## Send a chat to the server chat channel
            ## Send a discord message to the game admin discord

            active_server_players = serverPlayerController.get_list_active_by_server(server.key.id())
            for active_server_player in active_server_players:
                logging.info('found active server player - deactivating')
                active_server_player.active = False
                serverPlayerController.update(active_server_player)

            if game.characters_enabled:
                logging.info('characters are enabled')

                more = True

                while more:
                    ## get characters that  have this server selected
                    game_player_characters, curs, more = gameCharacterController.list_locked_by_serverKeyId(server.key.id())

                    for game_player_character in game_player_characters:
                        logging.info('found locked by character - unlocking')
                        game_player_character.locked = False
                        game_player_character.locked_by_serverKeyId = None

                        gameCharacterController.update(game_player_character)

                        chat_msg = json.dumps({"type":"chat",
                                                "textMessage":"The Server crashed.",
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
                            URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, game_player_character.firebaseUser)
                            resp, content = http_auth.request(URL,
                                                ##"PATCH",
                                              "PUT", ## Write or replace data to a defined path,
                                              chat_msg,
                                              headers=headers)

                            logging.info(resp)
                            logging.info(content)
                        except:
                            logging.error('heroku error')

            else:
                logging.info('characters are not enabled')

                more = True

                while more:
                    ## get characters that  have this server selected
                    game_players, curs, more = gpController.list_locked_by_serverKeyId(server.key.id())

                    for game_player in game_players:
                        logging.info('found locked game player- unlocking')
                        game_player.locked = False
                        game_player.locked_by_serverKeyId = None

                        gpController.update(game_player)

                        chat_msg = json.dumps({"type":"chat",
                                                "textMessage":"The Server crashed.",
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
                            URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, game_player.firebaseUser)
                            resp, content = http_auth.request(URL,
                                                ##"PATCH",
                                              "PUT", ## Write or replace data to a defined path,
                                              chat_msg,
                                              headers=headers)

                            logging.info(resp)
                            logging.info(content)
                        except:
                            logging.error('heroku error')

            if game.discord_subscribe_errors and game.discord_webhook_admin:
                # grab the logs from the params if available
                crash_logs = self.request.get('logs', 'DID NOT FIND LOGS')
                logging.info(self.request)
                logging.info(crash_logs)



                ## discord has a maximum length for description of 2048 characters
                ## but we really want all of the logs
                ## so split it if it's bigger

                split_logs = []
                split_more = True
                remaining_logs = crash_logs

                while split_more:
                    logging.info('splitting logs')

                    if len(remaining_logs) < 2000:
                        logging.info('logs is less than 2k')
                        split_more = False
                        split_logs.append(remaining_logs)
                    else:
                        logging.info('remaining logs is more than 2k')
                        split_logs.append(remaining_logs[:1999])
                        remaining_logs = remaining_logs[1999:]

                for remaining_log in split_logs:
                    logging.info('sending discord message')

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Server CRASH: %s | %s | %s" % ( server.title, server_cluster.vm_zone, remaining_log)
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Server CRASH", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)

            ## Turn the server provisioned off
            server.continuous_server_provisioned = False
            serverController.update(server)

            ## Turn the Server Shard record to offline.
            if server.sharded_from_template:
                logging.info('this is a shard')

                server_shard_record = serverShardController.get_by_serverShardKeyId(server.key.id())
                if server_shard_record:
                    logging.info('found the server shard record')
                    server_shard_record.online = False
                    serverShardController.update(server_shard_record)


            ## start a task to dealoocate the VM
            taskUrl='/task/server/vm/deallocate'
            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': server_cluster.vm_project,
                                                                                    "zone": server_cluster.vm_zone,
                                                                                    "name": server.continuous_server_title,
                                                                                    "serverKeyId": server.key.id()
                                                                                }, countdown=2)









        # TODO - create server instance for billing

        else:
            logging.info('This is not a server - checking match')

            match = matchController.get_by_api_key(serverKeyId)

            if not match:
                logging.info('Not a match either - returning ambiguous error')
                return self.render_json_response(
                    authorization = True,
                    error= "There was an error."
                    )

            game = gameController.get_by_key_id(match.gameKeyId)

            if not game:
                logging.info('game not found')
                return self.render_json_response(
                    authorization = True,
                    error= "The game was not found."
                    )

            game_mode = gameModeController.get_by_key_id(match.gameModeKeyId)

            if not game_mode:
                logging.info('game_mode not found')
                return self.render_json_response(
                    authorization = True,
                    error= "The game_mode was not found."
                    )

            ## We have a match server that crashed.
            ## find the match players
            ## refund any admission fee
            ## Send a chat to the match players
            ## Send a discord to the game admin
            ## delete the match players
            ## delete any created channels
            ## delete the match

            match_chat_channels_to_delete = []

            match_chat_channel = chatChannelController.get_by_channel_type_refKeyId("match", match.key.id())
            if match_chat_channel:
                logging.info('found match chat channel')
                match_chat_channels_to_delete.append(match_chat_channel)

            if game.discord_subscribe_errors and game.discord_webhook_admin:
                # grab the logs from the params if available
                crash_logs = self.request.get('logs', 'DID NOT FIND LOGS')
                logging.info(self.request)
                logging.info(crash_logs)

                ## discord has a maximum length for description of 2048 characters
                ## but we really want all of the logs
                ## so split it if it's bigger

                split_logs = []
                split_more = True
                remaining_logs = crash_logs

                while split_more:
                    logging.info('splitting logs')

                    if len(remaining_logs) < 1500:
                        logging.info('logs is less than 1500')
                        split_more = False
                        split_logs.append(remaining_logs)
                    else:
                        logging.info('remaining logs is more than 1500')
                        split_logs.append(remaining_logs[:1499])
                        remaining_logs = remaining_logs[1499:]

                for remaining_log in split_logs:
                    logging.info('sending discord message')

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Matchmaker Server CRASH: %s | %s | %s" % ( match.title, match.continuous_server_zone, remaining_log)
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Server CRASH", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)


            match_players = matchPlayerController.get_list_by_matchKeyId(match.key.id())

            for match_player in match_players:
                logging.info('match player found')

                ## TODO special handling for tournament

                ## TODO special handling for metagame

                if game_mode.admissionFeePerPlayer > 0:
                    logging.info('admissionFeePerPlayer > 0')

                    if match_player.matchmakerPaidAdmission:
                        logging.info('matchmakerPaidAdmission')

                        description = "Match Server Crash Refund"

                        ## Create a transaction for the withdrawl -game
                        transaction = TransactionsController().create(
                            gameKeyId = game.key.id(),
                            gameTitle = game.title,
                            description = description,
                            amountInt = -game_mode.admissionFeePerPlayer,
                            transactionType = "game",
                            transactionClass = "admission fee refund",
                            transactionSender = True,
                            transactionRecipient = False,
                            submitted = True,
                            processed = False,
                            materialIcon = MATERIAL_ICON_ADMISSION_FEE,
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

                        ## create a transaction for the refund - user
                        description = "Admission Fee refund from: %s" %match.title
                        recipient_transaction = transactionController.create(
                            amountInt = game_mode.admissionFeePerPlayer,
                            userKeyId = match_player.userKeyId,
                            firebaseUser = match_player.firebaseUser,
                            description = description,
                            transactionType = "user",
                            transactionClass = "admission fee refund",
                            transactionSender = False,
                            transactionRecipient = True,
                            submitted = True,
                            processed = False,
                            materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                            materialDisplayClass = "md-primary"
                        )

                        pushable = lockController.pushable("user:%s"%match_player.userKeyId)
                        if pushable:
                            logging.info('user pushable')
                            taskUrl='/task/user/transaction/process'
                            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                "key_id": match_player.userKeyId
                                                                                            }, countdown=2)

                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":"The Match Server crashed.",
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
                    URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, match_player.firebaseUser)
                    resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      chat_msg,
                                      headers=headers)

                    logging.info(resp)
                    logging.info(content)
                except:
                    logging.error('heroku error')



                chat_message = "> Left match chat"

                ## get the team chat channel
                if match_player.teamKeyId:
                    logging.info('found teamKeyId')
                    match_team_chat_channel = chatChannelController.get_by_channel_type_refKeyId("matchteam", match_player.teamKeyId)
                    if match_team_chat_channel:
                        logging.info('found match_team_chat_channel')
                        chat_message = chat_message + " and match team chat"
                        ## keep track of it so we can delete it later
                        if not match_team_chat_channel in match_chat_channels_to_delete:
                            match_chat_channels_to_delete.append(match_team_chat_channel)
                        ## this happens in the task, but in this case, we want to do it right away so when the new chat channel list gets sent, these are not included.
                        match_team_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_team_chat_channel.key.id(), match_player.userKeyId )
                        if match_team_chat_channel_subscriber:
                            logging.info('found match_team_chat_channel_subscriber')
                            chatChannelSubscribersController.delete(match_team_chat_channel_subscriber)


                ##  Send out a text message to the player
                taskUrl='/task/chat/channel/list_changed'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': match_player.firebaseUser,
                                                                                'userKeyId': match_player.userKeyId,
                                                                                'textMessage': chat_message
                                                                                }, countdown = 2)

                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': match_player.firebaseUser,
                                                                                    "message": chat_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })


                ## delete the match player
                matchPlayerController.delete(match_player)






            ##
            ## delete all of the chat channels
            for match_chat_channel_to_delete in match_chat_channels_to_delete:
                chatChannelController.delete(match_chat_channel_to_delete)

            ## check to see if this game is in local testing mode
            if not game.match_deploy_vm_local_testing:
                logging.info('match local testing is off')

                ## start a task to dealoocate the VM
                taskUrl='/task/matchmaker/vm/deallocate'
                vmTitle = "m%s" %match.key.id()
                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': 'ue4topia',
                                                                                        "zone": match.continuous_server_zone,
                                                                                        "name": vmTitle,
                                                                                        "matchKeyId": match.key.id()
                                                                                    }, countdown=MATCHMAKER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS)

            # make it so that the check unused task will fail

            match.match_active = False
            match.match_provisioned = False
            match.match_creating = False
            #match.continuous_server_creating_timestamp = None
            match.match_destroying = True
            match.match_destroying_timestamp = datetime.datetime.now()
            match.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
            match.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
            match.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value

            ## TODO unmute this just testing
            matchController.update(match)

            ## create a server_instance record.
            created_datetime = match.created

            destroying_datetime = datetime.datetime.now()
            total_seconds = (destroying_datetime - created_datetime).total_seconds()
            if total_seconds < VM_INSTANCE_MINIMUM_SECONDS:
                total_seconds = VM_INSTANCE_MINIMUM_SECONDS

            ## round up
            billable_min_uptime = int((total_seconds+(-total_seconds%60))//60)

            serverInstance = serverInstancesController.create(
                #serverKeyId = server.key.id(),
                #serverTitle = server.title,
                gameKeyId = match.gameKeyId,
                gameTitle = match.gameTitle,

                machine_type = match.continuous_server_machine_type,
                region_name = match.continuous_server_region,

                continuous_server_creating_timestamp = created_datetime,
                continuous_server_destroying_timestamp = destroying_datetime,

                uptime_minutes_billable = billable_min_uptime,

                #serverClusterKeyId = server.serverClusterKeyId,
                ##serverClusterTitle = server.serverClusterTitle,

                #userKeyId = server.userKeyId,
                processed = False,
                instanceType = 'match'
            )




        return self.render_json_response(
            response_successful = True,
            response_message = "Processed Request"
            )
