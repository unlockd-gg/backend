import logging
import os
import datetime
import string
import uuid
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.game_levels import GameLevelsController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController
from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.games import GamesController

from configuration import *

class InfoHandler(BaseHandler):
    def post(self):
        """
        Send server info
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        Optional POST parameters:  session_host_address, session_id
        """

        serverController = ServersController()
        serverClusterController = ServerClustersController()
        ucontroller = UsersController()
        serverLinksController = ServerLinksController()
        chatChannelsController = ChatChannelsController()
        GameLevelController = GameLevelsController()
        serverShardController = ServerShardsController()
        serverShardPlaceholderController = ServerShardPlaceholderController()
        groupsController = GroupsController()
        gamesController = GamesController()
        groupGamesController = GroupGamesController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            ipAddress = os.environ["REMOTE_ADDR"]
            logging.info("ipAddress: %s"% ipAddress)
            logging.info("server key_id: %s"% server.key.id())

            dirty = False
            session_host_address = self.request.POST.get('session_host_address', None)
            session_id = self.request.POST.get('session_id', None)

            server.session_host_address = session_host_address
            server.session_id = session_id
            server.continuous_server_online = True

            serverController.update(server)

            ## get the server cluster
            server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)
            if not server_cluster:
                logging.info('server cluster not found')
                return

            ## set up for returning custom in-game texture
            ## get the game's default first
            game = gamesController.get_by_key_id(server.gameKeyId)
            if not game:
                logging.error('game not found')
                return
            ## defaulting to grey for testing
            custom_in_game_texture = game.group_custom_texture_default

            ## set the online flag in the server link only if it's  a normal server
            if not server.instanced_from_template:
                if not server.sharded_from_template:
                    target_server_links = serverLinksController.get_list_by_targetServerKeyId(server.key.id())
                    for link in target_server_links:
                        logging.info('Setting online in serverLink')
                        link.targetStatusOnline = True
                        link.hostConnectionLink = server.hostConnectionLink
                        serverLinksController.update(link)

            ## if it is a sharded server we need to run some logic before updating the link state
            ## Actually, since this is a sharded server coming online, we know there is room
            if server.sharded_from_template:

                target_server_links = serverLinksController.get_list_by_targetServerKeyId(server.sharded_from_template_serverKeyId)

                for link in target_server_links:
                    logging.info('Setting online in serverLink')
                    link.targetStatusOnline = True
                    #link.hostConnectionLink = server.hostConnectionLink
                    serverLinksController.update(link)

                ## Sharded servers coming online should notify any users with active placeholders assigned to this server.
                placeholders_assigned_to_this_server = serverShardPlaceholderController.get_serverAssigned_by_serverShardKeyId(server.key.id())
                for placeholder in placeholders_assigned_to_this_server:
                    logging.info('found a placeholder assigned here')

                    chat_message = "%s ready" %server.title
                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': placeholder.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })



            # update firebase
            if not server.invisible:
                logging.info('visible')
                if not server.invisible_developer_setting:
                    logging.info('visible-dev')
                    taskUrl='/task/server/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server.key.id()}, countdown = 2,)

            ## send text chat if this is an instanced server
            if server.instanced_from_template:
                if server.instance_server_configuration == 'user':
                    logging.info('this is an instanced user server - sending chat')

                    ## get the user:
                    server_instance_user = ucontroller.get_by_key_id(server.instanced_for_userKeyId)
                    if server_instance_user:
                        chat_message = "> Private server %s ready" %server.title
                        taskUrl='/task/chat/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': server_instance_user.firebaseUser,
                                                                                            "message": chat_message,
                                                                                            "created":datetime.datetime.now().isoformat()
                                                                                        })
                elif server.instance_server_configuration == 'party':
                    logging.info('this is an instanced party server - sending chat')

                    # get the party chat channel
                    party_chat_channel = chatChannelsController.get_by_channel_type_refKeyId('team', server.instanced_for_partyKeyId)
                    if party_chat_channel:
                        chat_message = "Party server %s ready" %server.title

                        taskUrl='/task/chat/channel/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': party_chat_channel.key.id(),
                                                                                            "message": chat_message,
                                                                                            #"userKeyId": authorized_user.key.id(),
                                                                                            #"userTitle": authorized_user.title,
                                                                                            "chatMessageKeyId": uuid.uuid4(),
                                                                                            "chatChannelTitle": party_chat_channel.title,
                                                                                            "chatChannelRefType":party_chat_channel.channel_type,
                                                                                            "created":datetime.datetime.now().isoformat()
                                                                                        })
                elif server.instance_server_configuration == 'group':
                    logging.info('this is an instanced group server - sending chat')

                    ## grab the group's custom texture url
                    group_game = groupGamesController.get_by_groupKeyId_gameKeyId(server.instanced_for_groupKeyId, server.gameKeyId)
                    if group_game:
                        if group_game.inGameTextureServingUrl:
                            custom_in_game_texture = group_game.inGameTextureServingUrl

                    # get the party chat channel
                    group_chat_channel = chatChannelsController.get_by_channel_type_refKeyId('group', server.instanced_for_groupKeyId)
                    if group_chat_channel:
                        chat_message = "Group server %s ready" %server.title

                        taskUrl='/task/chat/channel/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': group_chat_channel.key.id(),
                                                                                            "message": chat_message,
                                                                                            #"userKeyId": authorized_user.key.id(),
                                                                                            #"userTitle": authorized_user.title,
                                                                                            "chatMessageKeyId": uuid.uuid4(),
                                                                                            "chatChannelTitle": group_chat_channel.title,
                                                                                            "chatChannelRefType": group_chat_channel.channel_type,
                                                                                            "created": datetime.datetime.now().isoformat()
                                                                                        })

            # Get the game level
            gameLevel = "unknown"
            if server.gameLevelKeyId:
                game_level_record = GameLevelController.get_by_key_id(server.gameLevelKeyId)
                if game_level_record:
                    gameLevel = game_level_record.engineTravelUrlString

            if server.server_last_running_timestamp:
                last_running_timestamp = server.server_last_running_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                last_running_timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

            ## if this is a shard, update the server shard record
            if server.sharded_from_template:
                logging.info('found a shard - updating server_shard record')

                server_shard = serverShardController.get_by_serverShardKeyId(server.key.id())
                if server_shard:
                    server_shard.online = True
                    server_shard.playerCount = 0
                    server_shard.hostConnectionLink = server.hostConnectionLink
                    serverShardController.update(server_shard)
                else:
                    logging.error('no server shard record found for a server marked as sharded')

            datetime_iso = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

            return self.render_json_response(
                authorization = True,
                incrementCurrency = server.incrementCurrency,
                minimumCurrencyRequired= server.minimumCurrencyHold,
                admissionFee = server.admissionFee,
                title = server.title,
                serverCurrency = server.serverCurrency,
                gameLevel = gameLevel,
                last_running_timestamp = last_running_timestamp,
                serverTime = datetime_iso,
                sharded = server.sharded_from_template,
                custom_in_game_texture = custom_in_game_texture,
                configuration = server.configuration,
                api_version = 1,
                region = server_cluster.vm_region
            )
