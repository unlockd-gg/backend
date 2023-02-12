import endpoints
import logging
import uuid
import urllib
import json
import random
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

##from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.game_levels import GameLevelsController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.models.servers import *
from apps.uetopia.models.server_clusters import *
from apps.uetopia.models.server_links import *
from apps.uetopia.models.server_players import *

from apps.uetopia.providers.compute_engine_zonemap import region_zone_mapper

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="servers", version="v1", description="Servers API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class ServersApi(remote.Service):
    @endpoints.method(SERVER_CREATE_RESOURCE, ServerDeveloperResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        """ Create a new server - PROTECTED """
        logging.info("serverCreate")


        gcontroller = GamesController()
        scontroller = ServersController()
        usersController = UsersController()
        serverClusterController = ServerClustersController()
        gameLevelController = GameLevelsController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerDeveloperResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerDeveloperResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerDeveloperResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerDeveloperResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        try:
            game = gcontroller.get_by_key_id(request.gameKeyId)
            if not game:
                logging.error('game not found')
                return ServerDeveloperResponse(response_message='Error: Game not found. ', response_successful=False)
        except:
            logging.error('game not found')
            return ServerDeveloperResponse(response_message='Error: gameKeyId not found. ', response_successful=False)

        try:
            game_level = gameLevelController.get_by_key_id(request.gameLevelKeyId)
            if not game_level:
                logging.error('game level not found')
                return ServerDeveloperResponse(response_message='Error: Game Level not found. ', response_successful=False)
        except:
            logging.error('game level not found')
            return ServerDeveloperResponse(response_message='Error: gameLevelKeyId not found. ', response_successful=False)

        if request.serverClusterKeyId:
            server_cluster = serverClusterController.get_by_key_id(request.serverClusterKeyId)
            if server_cluster:
                sc_key_id = server_cluster.key.id()
            else:
                sc_key_id = None
        else:
            sc_key_id = None

        server = scontroller.create(
            title = request.title,
            description = request.description,
            hostAddress = request.hostAddress,
            hostPort = request.hostPort,
            hostConnectionLink = request.hostConnectionLink,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            #maxActivePlayers = request.maxActivePlayers,
            #maxAuthorizedPlayers = request.maxAuthorizedPlayers,
            #googleUser = str(current_user),
            userKeyId = authorized_user.key.id(),
            minimumCurrencyHold = request.minimumCurrencyHold or SERVER_CREATE_DEFAULT_MINIMUMCURRENCYHOLD,
            totalCurrencyHeld = 0,
            incrementCurrency = request.incrementCurrency or SERVER_CREATE_DEFAULT_INCREMENTCURRENCY,
            currencyAwarded = 0,
            apiKey = scontroller.create_unique_api_key(),
            apiSecret = scontroller.key_generator(),
            continuous_server_provisioned = False,
            continuous_server_entry = True,
            continuous_server_creating = False,
            continuous_server_active = False,
            serverInfoRefreshNeeded = False,
            invisible = False,
            invisible_developer_setting = False,
            admissionFee = request.admissionFee,
            serverClusterKeyId = sc_key_id,
            session_host_address = request.session_host_address,
            session_id = request.session_id,

            infinite_server_unused = request.infinite_server_unused,
            gameLevelKeyId = game_level.key.id(),
            gameLevelTitle =game_level.title,

            server_to_game_transfer_threshold = server_cluster.server_to_game_transfer_threshold,
            travelMode = server_cluster.travelMode,
            randomRef = random.random(),
            serverCurrency = 0,
            requireBadgeTags = request.requireBadgeTags
        )

        ## set up the chat channel
        server_chat_title = request.title + " chat"
        chat_channel = ChatChannelsController().create(
            title = server_chat_title,
            #text_enabled = True,
            #data_enabled = False,
            channel_type = 'server',
            adminUserKeyId = authorized_user.key.id(),
            refKeyId = server.key.id(),
            gameKeyId = game.key.id(),
            max_subscribers = 200
        )

        return ServerDeveloperResponse(
                            key_id = server.key.id(),
                            title = server.title,
                            description = server.description,
                            gameKeyId = server.gameKeyId,
                            incrementCurrency = server.incrementCurrency,
                            minimumCurrencyHold = server.minimumCurrencyHold,
                            currencyAwarded = server.currencyAwarded,
                            iconServingUrl = server.iconServingUrl,
                            bannerServingUrl = server.bannerServingUrl,
                            cssServingUrl = server.cssServingUrl,
                            lastMapTitle = server.lastMapTitle,
                            admissionFee = server.admissionFee,
                            #players = "",## prepare angular to deal with the players array.  sending a string for now
                            hostAddress = server.hostAddress,
                            hostPort = server.hostPort,
                            hostConnectionLink = server.hostConnectionLink,
                            apiKey = server.apiKey,
                            apiSecret = server.apiSecret,
                            response_message = 'Server Created. ',
                            response_successful = True
                            )


    @endpoints.method(SERVER_COLLECTION_PAGE_RESOURCE, ServerCollection, path='serversCollectionGetPage', http_method='POST', name='collection.get.page')
    def serversCollectionGetPage(self, request):
        """ Get a collection of servers - Pass serverClusterKeyId, sharded_from_template_serverKeyId or gameKeyId to filter, otherwise returning all publicly viewable servers """
        logging.info("serversCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerCollection(response_message='Error: No User Record Found. ', response_successful=False)

        serversController = ServersController()

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        sort_order = request.sort_order
        direction = request.direction

        if request.serverClusterKeyId:
            logging.info('serverClusterKeyId found')
            entities, cursor, more = serversController.list_page_not_instanced_sharded_by_serverClusterKeyId(request.serverClusterKeyId, start_cursor=curs)

        elif request.serverClusterKeyIdStr:
            logging.info('serverClusterKeyIdStr found')
            entities, cursor, more = serversController.list_page_not_instanced_sharded_by_serverClusterKeyId(int(request.serverClusterKeyIdStr), start_cursor=curs)

        elif request.gameKeyId:
            logging.info('gameKeyId found')
            entities, cursor, more = serversController.list_page_by_gameKeyId(request.gameKeyId, start_cursor=curs)

        elif request.sharded_from_template_serverKeyId:
            logging.info('sharded_from_template_serverKeyId')
            entities, cursor, more = serversController.list_page_by_sharded_from_template_serverKeyId(request.sharded_from_template_serverKeyId, start_cursor=curs)

        elif request.instanced_from_template_serverKeyId:
            logging.info('instanced_from_template_serverKeyId')
            entities, cursor, more = serversController.list_page_by_instanced_from_template_serverKeyId(request.instanced_from_template_serverKeyId, start_cursor=curs)

        else:
            entities, cursor, more = serversController.list_page(start_cursor=curs)

        entity_list = []

        for entity in entities:
            entity_list.append(ServerResponse(
                key_id = entity.key.id(),
                key_id_str = str(entity.key.id()),
                title = entity.title,
                description = entity.description,
                continuous_server = entity.continuous_server,
                continuous_server_provisioned = entity.continuous_server_provisioned,
                continuous_server_active = entity.continuous_server_active,
                #continuous_server_region = entity.continuous_server_region
            ))

        if cursor:
            cursor_urlsafe = cursor.urlsafe()
        else:
            cursor_urlsafe = None

        response = ServerCollection(
            servers = entity_list,
            more = more,
            cursor = cursor_urlsafe,
            response_successful = True,
            response_message = "Success.  Returning server list."
        )

        return response


    @endpoints.method(SERVER_GET_RESOURCE, ServerResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a single server.  If the requested server is owned by the user making the request, return developer details """
        logging.info("serversGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        serversController = ServersController()

        if not request.key_id:
            return ServerResponse(response_message="key_id is required")

        entity = serversController.get_by_key_id(int(request.key_id))

        if entity.userKeyId == authorized_user.key.id():
            ## send all of the developer data
            response = ServerResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                gameKeyId = entity.gameKeyId,
                serverClusterKeyId = entity.serverClusterKeyId,
                minimumCurrencyHold = entity.minimumCurrencyHold,
                admissionFee = entity.admissionFee,
                invisible = entity.invisible,
                invisible_developer_setting = entity.invisible_developer_setting,
                bannerServingUrl = entity.bannerServingUrl,
                apiKey = entity.apiKey,
                apiSecret = entity.apiSecret,
                #hostAddress = entity.hostAddress,
                hostConnectionLink = entity.hostConnectionLink,
                session_host_address = entity.session_host_address,
                session_id = entity.session_id,
                continuous_server = entity.continuous_server,
                continuous_server_provisioned = entity.continuous_server_provisioned,
                ## moved to server clusters
                #continuous_server_project = entity.continuous_server_project,
                #continuous_server_bucket = entity.continuous_server_bucket,
                #continuous_server_zone = entity.continuous_server_zone,
                #continuous_server_region = entity.continuous_server_region,
                #continuous_server_source_disk_image = entity.continuous_server_source_disk_image,
                #continuous_server_machine_type = entity.continuous_server_machine_type,
                #continuous_server_startup_script_location = entity.continuous_server_startup_script_location,
                #continuous_server_shutdown_script_location = entity.continuous_server_shutdown_script_location,
                continuous_server_entry = entity.continuous_server_entry,
                infinite_server_unused = entity.infinite_server_unused,
                gameLevelKeyId = entity.gameLevelKeyId,
                server_to_game_transfer_threshold = entity.server_to_game_transfer_threshold,
                randomRef = entity.randomRef,

                instance_server_template = entity.instance_server_template,
                instance_server_purge_after_use = entity.instance_server_purge_after_use,
                instance_server_purge_delay_seconds = entity.instance_server_purge_delay_seconds,
                instance_server_configuration = entity.instance_server_configuration,
                instance_party_size_maximum = entity.instance_party_size_maximum,
                instanced_from_template = entity.instanced_from_template,

                instanced_for_userKeyId = entity.instanced_for_userKeyId,
                instanced_for_userTitle = entity.instanced_for_userTitle,
                instanced_for_partyKeyId = entity.instanced_for_partyKeyId,
                instanced_for_partyTitle = entity.instanced_for_partyTitle,
                instanced_for_groupKeyId = entity.instanced_for_groupKeyId,
                instanced_for_groupTitle = entity.instanced_for_groupTitle,

                sharded_server_template = entity.sharded_server_template,
                shard_count_maximum = entity.shard_count_maximum,
                sharded_player_capacity_threshold = entity.sharded_player_capacity_threshold,
                sharded_player_capacity_maximum = entity.sharded_player_capacity_maximum,
                sharded_from_template = entity.sharded_from_template,

                vendors_allowed = entity.vendors_allowed,
                player_created_vendors_allowed = entity.player_created_vendors_allowed,

                configuration = entity.configuration,

                drop_items_permitted = entity.drop_items_permitted,
                pickup_items_permitted = entity.pickup_items_permitted,

                requireBadgeTags = entity.requireBadgeTags,

                response_message='Success.',
                response_successful=True
            )

        else:
            response = ServerResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                gameKeyId = entity.gameKeyId,
                serverClusterKeyId = entity.serverClusterKeyId,
                bannerServingUrl = entity.bannerServingUrl,
                minimumCurrencyHold = entity.minimumCurrencyHold,
                admissionFee = entity.admissionFee,
                invisible_developer_setting = entity.invisible_developer_setting,
                #hostAddress = entity.hostAddress,
                hostConnectionLink = entity.hostConnectionLink,
                session_host_address = entity.session_host_address,
                session_id = entity.session_id,
                randomRef = entity.randomRef,
                requireBadgeTags = entity.requireBadgeTags,
                response_message='Success.',
                response_successful=True
            )

        return response

    @endpoints.method(SERVER_EDIT_RESOURCE, ServerResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update a server.  Restricted to the developer account. - PROTECTED """
        logging.info("serversUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        serversController = ServersController()
        serverLinkController = ServerLinksController()
        serverShardController = ServerShardsController()

        if not request.key_id:
            return ServerResponse(response_message="key_id is required", response_successful=False)

        entity = serversController.get_by_key_id(int(request.key_id))

        dirty = False

        logging.info(request.invisible)

        ## Admin check
        if request.adminRequest:
            if authorized_user.admin:
                logging.info('Admin found - Setting admin only fields.')
                dirty = True
                entity.invisible_developer_setting = request.invisible_developer_setting
                entity.invisible = request.invisible

        ## owner check
        if entity.userKeyId == authorized_user.key.id():
            dirty = True

            entity.title = request.title
            entity.description = request.description

            entity.minimumCurrencyHold = request.minimumCurrencyHold
            entity.invisible_developer_setting = request.invisible_developer_setting
            entity.admissionFee = request.admissionFee
            entity.hostAddress = request.hostAddress
            entity.hostConnectionLink = request.hostConnectionLink
            entity.bannerServingUrl = request.bannerServingUrl

            entity.session_host_address = request.session_host_address
            entity.session_id = request.session_id

            entity.continuous_server= request.continuous_server

            ## moved to server clusters
            #entity.continuous_server_project = request.continuous_server_project
            #entity.continuous_server_bucket = request.continuous_server_bucket
            #entity.continuous_server_zone = region_zone_mapper(request.continuous_server_region)
            #entity.continuous_server_region = request.continuous_server_region
            #entity.continuous_server_source_disk_image = request.continuous_server_source_disk_image
            #entity.continuous_server_machine_type = request.continuous_server_machine_type
            #entity.continuous_server_startup_script_location = request.continuous_server_startup_script_location
            #entity.continuous_server_shutdown_script_location = request.continuous_server_shutdown_script_location

            entity.continuous_server_entry = request.continuous_server_entry
            entity.continuous_server_provisioned = request.continuous_server_provisioned

            entity.infinite_server_unused = request.infinite_server_unused
            entity.gameLevelKeyId = request.gameLevelKeyId
            entity.server_to_game_transfer_threshold = request.server_to_game_transfer_threshold
            entity.randomRef = request.randomRef

            entity.instance_server_template = request.instance_server_template
            entity.instance_server_purge_after_use = request.instance_server_purge_after_use
            entity.instance_server_purge_delay_seconds = request.instance_server_purge_delay_seconds
            entity.instance_server_configuration = request.instance_server_configuration
            entity.instance_party_size_maximum = request.instance_party_size_maximum

            entity.sharded_server_template = request.sharded_server_template
            entity.shard_count_maximum = request.shard_count_maximum
            entity.sharded_player_capacity_threshold = request.sharded_player_capacity_threshold
            entity.sharded_player_capacity_maximum = request.sharded_player_capacity_maximum

            entity.vendors_allowed = request.vendors_allowed
            entity.player_created_vendors_allowed = request.player_created_vendors_allowed

            entity.configuration = request.configuration

            entity.drop_items_permitted = request.drop_items_permitted
            entity.pickup_items_permitted = request.pickup_items_permitted

            entity.requireBadgeTags = request.requireBadgeTags


        if dirty:
            serversController.update(entity)

            ## update serverlink too - title at least needs to change
            server_links = serverLinkController.get_list_by_targetServerKeyId(entity.key.id())
            for server_link in server_links:
                logging.info('updating target link')
                server_link.targetServerTitle = entity.title
                server_link.targetInstanced = entity.instance_server_template
                server_link.targetInstanceConfiguration = entity.instance_server_configuration
                server_link.targetInstancePartySizeMaximum = entity.instance_party_size_maximum

                ## also set the link to provisioned online
                if entity.continuous_server_provisioned:
                    server_link.targetStatusProvisioned = True
                    server_link.targetStatusOnline = True

                serverLinkController.update(server_link)

            ## if it's an instance template, update the previously instanced servers too.
            ## TODO move this to a task so we can handle more than 1000
            instanced_servers, cursor, more = serversController.list_page_by_instanced_from_template_serverKeyId(entity.key.id())
            for instanced_server in instanced_servers:
                logging.info('updating existing instance')
                instanced_server.minimumCurrencyHold = entity.minimumCurrencyHold
                instanced_server.admissionFee = entity.admissionFee
                instanced_server.server_to_game_transfer_threshold = entity.server_to_game_transfer_threshold
                instanced_server.gameLevelKeyId = entity.gameLevelKeyId
                instanced_server.continuous_server_machine_type = entity.continuous_server_machine_type
                instanced_server.continuous_server_source_disk_image = entity.continuous_server_source_disk_image
                instanced_server.continuous_server_startup_script_location = entity.continuous_server_startup_script_location
                instanced_server.continuous_server_shutdown_script_location = entity.continuous_server_shutdown_script_location

                instanced_server.vendors_allowed = entity.vendors_allowed
                instanced_server.player_created_vendors_allowed = entity.player_created_vendors_allowed

                instanced_server.drop_items_permitted = entity.drop_items_permitted
                instanced_server.pickup_items_permitted = entity.pickup_items_permitted
                instanced_server.requireBadgeTags = entity.requireBadgeTags

                serversController.update(instanced_server)

            if more:
                logging.error('too many instances to update without a task.  TODO make the task')

            ##  update sharded servers too.

            if entity.sharded_server_template:
                logging.info('this is a sharded server template - updating shards')
                sharded_servers, cursor, more = serversController.list_page_by_sharded_from_template_serverKeyId(entity.key.id())

                for sharded_server in sharded_servers:
                    logging.info('found sharded server')

                    sharded_server.sharded_player_capacity_threshold = entity.sharded_player_capacity_threshold
                    sharded_server.sharded_player_capacity_maximum = entity.sharded_player_capacity_maximum

                    serversController.update(sharded_server)

                    ## update the shard record too.
                    server_shard = serverShardController.get_by_serverShardKeyId(sharded_server.key.id())

                    if server_shard:
                        logging.info('got server shard record')

                        server_shard.playerCapacityThreshold = sharded_server.sharded_player_capacity_threshold
                        server_shard.playerCapacityMaximum = sharded_server.sharded_player_capacity_maximum

                        serverShardController.update(server_shard)



            ## for shards that are sharded_from_template we might need to change the server_shard record .
            ## this is mostly to enable local testing of a shard
            ## the incoming query to fetch all servers will be looking at this server_shard model to find online shards

            ## this already happens in server/info
            """
            if entity.sharded_from_template:
                logging.info('found shard server')
                if entity.continuous_server_provisioned:
                    shard_online = True
                else:
                    shard_online = False

                server_shard = serverShardController.get_by_serverShardKeyId(entity.key.id())
                if server_shard:
                    logging.info('updating server_shard')
                    server_shard.online = shard_online
                    serverShardController.update(server_shard)
            """

        ## make sure this server has a chat channel - legacy support - TODO remove this when we're sure all servers have channels.
        ## instance templates do not need
        if not entity.instance_server_template:
            chatChannelController = ChatChannelsController()
            existing_chat_channel = chatChannelController.get_by_channel_type_refKeyId('server', entity.key.id())
            if existing_chat_channel:
                ## check to see if there is a gameKeyId
                if not existing_chat_channel.gameKeyId:
                    existing_chat_channel.gameKeyId = gameKeyId = entity.gameKeyId
                    chatChannelController.update(existing_chat_channel)
            else:
                ## set up the chat channel
                server_chat_title = entity.title + " chat"
                chat_channel = chatChannelController.create(
                    title = server_chat_title,
                    #text_enabled = True,
                    #data_enabled = False,
                    channel_type = 'server',
                    adminUserKeyId = authorized_user.key.id(),
                    refKeyId = entity.key.id(),
                    gameKeyId = entity.gameKeyId,
                    max_subscribers = 200
                )

        response = ServerResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            response_message='Success.  Server updated.',
            response_successful=True
        )

        remove_from_firebase = True

        if not entity.invisible:
            logging.info('visible')
            if not entity.invisible_developer_setting:
                logging.info('visible-dev')
                remove_from_firebase = False
                taskUrl='/task/server/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': entity.key.id()}, countdown = 2,)

        ##  try to delete invisible from firebase
        if remove_from_firebase:
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

            http_auth = credentials.authorize(Http())

            logging.info('processing program')

            headers = {"Content-Type": "application/json"}

            URL = "https://ue4topia.firebaseio.com/servers/%s.json" % entity.key.id()
            logging.info(URL)

            logging.info('deleting the server from firebase')
            resp, content = http_auth.request(URL,
                          "DELETE", ## We can delete data with a DELETE request
                          "",
                          headers=headers)

            URL = "https://ue4topia.firebaseio.com/games/%s/servers/%s.json" % (entity.gameKeyId, entity.key.id())
            logging.info(URL)

            logging.info('deleting the server from game firebase')
            resp, content = http_auth.request(URL,
                          "DELETE", ## We can delete data with a DELETE request
                          "",
                          headers=headers)

        return response

    @endpoints.method(SERVER_GET_RESOURCE, ServerResponse, path='delete', http_method='POST', name='delete')
    def delete(self, request):
        """ Delete a server - restricted to developer - PROTECTED """
        logging.info("serversDelete")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        serverLinksController = ServerLinksController()
        serversController = ServersController()
        chatChannelController = ChatChannelsController()

        if not request.key_id:
            return ServerResponse(response_message="key_id is required", response_successful=False)

        entity = serversController.get_by_key_id(int(request.key_id))

        if entity:
            if entity.userKeyId == authorized_user.key.id():

                if entity.continuous_server_provisioned:
                    logging.info('server is provisioned -aborting')
                    return ServerResponse(key_id = servercluster.key.id(),
                         response_message='server NOT Deleted.  It is propvisioned. ', response_successful=False
                         )

                if entity.continuous_server_creating:
                    logging.info('server is creating -aborting')
                    return ServerResponse(key_id = servercluster.key.id(),
                            response_message='serverNOT Deleted.  It is creating. ', response_successful=False
                            )

                if entity.serverCurrency < 0:
                    logging.info('server balance is below zero -aborting')
                    return ServerResponse(key_id = servercluster.key.id(),
                            response_message='server NOT Deleted.  It has a negative balance. ', response_successful=False
                            )

                ## TODO - check all of the links and balances and such
                curs = Cursor()
                server_links, cursor, more = serverLinksController.list_page_by_userKeyId_originServerKeyId(entity.userKeyId, entity.key.id(), start_cursor=curs)

                for server_link in server_links:
                    logging.info("found a server link to delete.")

                    serverLinksController.delete(server_link)

                ## delete the chat channel
                chat_channel = chatChannelController.get_by_channel_type_refKeyId('server', entity.key.id())
                if chat_channel:
                    logging.info('found chat channel to delete')
                    chatChannelController.delete(chat_channel)

                serversController.delete(entity)

                return ServerResponse(response_message='Success.', response_successful=True)
            else:
                return ServerResponse(response_message='Error: You are not the owner of this game.', response_successful=False)
        else:
            return ServerResponse(response_message='Error: Servers not found.', response_successful=False)


    ## SERVER PLAYERS

    @endpoints.method(SERVER_AUTHORIZE_RESOURCE, ServerAuthorizeResponse, path='serverPlayStart', http_method='POST', name='play.start')
    def serverPlayStart(self, request):
        """ Play Start - Create or update game player preferences - This also checks for online servers and brings one online if needed """
        logging.info("serverPlayStart")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerAuthorizeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        server_controller = ServersController()
        spmController = ServerPlayersController()
        usersController = UsersController()
        server_player_controller = ServerPlayersController()

        currency_hold = request.currencyHold
        key_id = int(request.key_id)

        logging.info('currency_hold: %s' %currency_hold)
        logging.info('key_id: %s' %key_id)

        if currency_hold < 1:
            logging.error('Error: Minimum hold is 1.')
            return ServerAuthorizeResponse(response_message='Error: Minimum hold is 1.', response_successful=False)


        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerAuthorizeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerAuthorizeResponse(response_message='Error: No User Record Found. ', response_successful=False)


        server_player = spmController.get_server_user(key_id, authorized_user.key.id())
        authorizedServerPlayers = spmController.get_list_authorized_by_server(key_id)
        server = server_controller.get_by_key_id(key_id)

        ## make sure the user has not already authorized.  Prevent duplicate transactions.
        if server_player:
            if server_player.authorized:
                ## update the server player so they show in the playerlist
                server_player.authCount = server_player.authCount +1
                spmController.update(server_player)

                ##  update firebase server player record
                taskUrl='/task/server/player/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id()}, countdown = 2,)

                return ServerAuthorizeResponse(response_message='Error: You are already authorized on this server.  Sending server data.', response_successful=False)

        if authorizedServerPlayers:
            logging.info('authorizedServerPlayers found')
            if len(authorizedServerPlayers) >= server.maxAuthorizedPlayers:
                logging.info("This server cannot accept any more authorizations at this time. ")


        logging.info("authorized_user.currencyBalance: %s"% authorized_user.currencyBalance)
        logging.info("currency_hold: %s" %currency_hold)

        ## verify that the player has enough non-hold btc to cover it
        if authorized_user.currencyBalance >= currency_hold:
            logging.info('authorized_user.currencyBalance >= currency_hold')

            ## verify that the selected hold amount is greater than the minimum
            if server.minimumCurrencyHold <= currency_hold:
                ## perform the authorization
                logging.info('Checks passed.  Adding pending server authorization')

                lockController = TransactionLockController()
                game_player_controller = GamePlayersController()

                ## - adjust the held btc down
                ## this happens in transaction processing, not here.
                #authorized_user.currencyBalance = authorized_user.currencyBalance - currency_hold

                #usersController.update(authorized_user)

                description = "Joined Server %s" %server.title

                ## Create a transaction for the withdrawl -user
                transaction = TransactionsController().create(
                    userKeyId = authorized_user.key.id(),
                    firebaseUser = authorized_user.firebaseUser,
                    description = description,
                    ##confirmations = 0,
                    amountInt = -currency_hold,
                    #serverKeyId = server.key.id(),
                    #serverTitle = server.title,
                    ##amount = currency_hold / 100000000. * -1,
                    #newBalanceInt = authorized_user.currencyBalance,
                    #newBalance = float(authorized_user.currencyBalance) / 100000000.
                    transactionType = "user",
                    transactionClass = "server activate",
                    transactionSender = True,
                    transactionRecipient = False,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_SERVER_AUTHORIZE,
                    materialDisplayClass = "md-accent"
                    )

                pushable = lockController.pushable("user:%s"%authorized_user.key.id())
                if pushable:
                    logging.info('user pushable')
                    taskUrl='/task/user/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": authorized_user.key.id()
                                                                                    }, countdown=2)

                ## The server does not actually get a transaction here.  It's just the user withdrawal that is moved over to the server player

                if server_player:
                    server_player.authTimestamp = datetime.datetime.now()
                    server_player.authCount = server_player.authCount + 1
                    server_player.pending_authorize = True
                    server_player.authorized = True
                    server_player.currencyStart = currency_hold
                    server_player.currencyCurrent = currency_hold
                    #server_player.avatar_theme = player.avatar_theme
                    server_player.userTitle = authorized_user.title

                    spmController.update(server_player)
                else:

                    ## Create the server player member
                    server_player = spmController.create(
                        authTimestamp = datetime.datetime.now(),
                        authCount = 1,
                        deAuthCount = 0,
                        serverKeyId = server.key.id(),
                        serverTitle = server.title,
                        gameKeyId = server.gameKeyId,
                        gameTitle = server.gameTitle,
                        currencyStart = currency_hold,
                        currencyCurrent = currency_hold,
                        userKeyId = authorized_user.key.id(),
                        userTitle = authorized_user.title,
                        firebaseUser = authorized_user.firebaseUser,
                        pending_authorize = True,
                        pending_deauthorize = False,
                        authorized = True,
                        active = False,
                        banned = False,
                        ladderRank = 1600,
                        #internal_matchmaker = False,
                        #avatar_theme = player.avatar_theme
                    )

                ## Make sure there is a game player member record
                existing_game_player = game_player_controller.get_by_gameKeyId_userKeyId(server.gameKeyId, authorized_user.key.id())
                if not existing_game_player:
                    logging.info("Game player NOT found.  Creating one.")

                    new_game_player = game_player_controller.create(
                        gameKeyId = server.gameKeyId,
                        gameTitle = server.gameTitle,
                        userKeyId = authorized_user.key.id(),
                        userTitle = authorized_user.title,
                        #playerAvatarTheme = player.avatar_theme,
                        locked = False,
                        online = True,
                        rank = 1600,
                        score = 0,
                    )

                ##  update firebase server player record
                taskUrl='/task/server/player/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id()}, countdown = 2,)

                ## check to see if this is a dedicated_dynamic server that is not spun up
                if server.continuous_server:
                    logging.info("continuous_server")
                    if not server.continuous_server_creating:
                        if not server.continuous_server_provisioned:
                            logging.info('Creating new instance to host this server')

                            ## start a task to create the vm
                            taskUrl='/task/server/vm/allocate'
                            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                    "serverKeyId": server.key.id()
                                                                                                })

                return ServerAuthorizeResponse(
                        key_id = server.key.id(),
                        response_message='Success.  Joined the server.',
                        response_successful=True

                        )

            else:
                logging.info("Minimum hold not put in")
                return ServerAuthorizeResponse(
                        key_id = None,

                        response_successful = False,
                        response_message = "Error: Minimum hold not put in"
                        )

        else:
            return ServerAuthorizeResponse(
                                    key_id = None,
                                    response_successful = False,
                                    response_message = "Error: Insufficent balance."
                                    )

    @endpoints.method(SERVER_GET_RESOURCE, ServerAuthorizeResponse, path='serverPlayEnd', http_method='POST', name='play.end')
    def serverPlayEnd(self, request):
        """ End play on a server """
        logging.info("serverPlayEnd")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerAuthorizeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        key_id = int(request.key_id)

        server_controller = ServersController()

        spmController = ServerPlayersController()
        usersController = UsersController()
        server_player_controller = ServerPlayersController()

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerAuthorizeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerAuthorizeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        server = server_controller.get_by_key_id(key_id)

        ## Get the server player member record if any.
        server_player_member = server_player_controller.get_server_user(key_id, authorized_user.key.id())

        ## verify that the server_player_member exists
        if server_player_member:
            logging.info('server_player_member')

            if server_player_member.active:
                logging.info('server_player_member is Active')

                return ServerAuthorizeResponse(
                                        serverKeyId = None,
                                        response_successful = False,
                                        response_message = "Error: server_player_member is Active."
                                        )

            else:
                logging.info('server_player_member is NOT Active')
                ## Mark the server player member as pending deactivate
                server_player_member.pending_deauthorize = True
                server_player_member.deAuthTimestamp = datetime.datetime.now()
                server_player_controller.update(server_player_member)


                taskUrl='/task/server/player/deauthorize'
                taskqueue.add(url=taskUrl, queue_name='serverDeauthorize', params={'key_id': server_player_member.key.id()
                                                                                    }, countdown=SERVER_DEAUTHORIZE_TIMEOUT_SECONDS)

                return ServerAuthorizeResponse(
                                        key_id = server.key.id(),
                                        response_successful = True,
                                        response_message='Deactivation Requested.  Stand by.'
                                        )
        else:
            return ServerAuthorizeResponse(
                                    key_id = None,
                                    response_successful = False,
                                    response_message='Error: Deactivation Request Failed.'
                                    )


    ##################
    ## Server Clusters
    ##################

    @endpoints.method(SERVER_CLUSTER_CREATE_RESOURCE, ServerClusterResponse, path='serverClusterCreate', http_method='POST', name='cluster.create')
    def serverClusterCreate(self, request):
        """ Create a server cluster - restricted to developer - PROTECTED """
        logging.info("serverClusterCreate")

        serverClusterController = ServerClustersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerClusterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerClusterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerClusterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerClusterResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        logging.info(request.gameKeyId)

        serverCluster = serverClusterController.create(
            title = request.title,
            description = request.description,
            max_count = request.max_count,
            min_online = request.min_online,
            gameKeyId = request.gameKeyId,
            groupCluster = request.groupCluster,
            groupKeyId = request.groupKeyId,
            groupTitle = request.groupTitle,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            serverCreationMode = request.serverCreationMode,
            server_to_game_transfer_threshold = request.server_to_game_transfer_threshold,
            game_to_server_initial_transfer_amount = request.game_to_server_initial_transfer_amount,
            travelMode = request.travelMode,
            newPlayerStartMode = request.newPlayerStartMode,
            rejoiningPlayerStartMode = request.rejoiningPlayerStartMode
        )

        ## update firebase
        taskUrl='/task/servercluster/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': serverCluster.key.id(), 'gameKeyId': serverCluster.gameKeyId }, countdown = 2,)

        return ServerClusterResponse(
                        key_id = serverCluster.key.id(),
                        response_message = "Success.  Server Cluster Created.", response_successful=True
                        )

    @endpoints.method(SERVER_CLUSTER_EDIT_RESOURCE, ServerClusterResponse, path='serverClustersGet', http_method='POST', name='cluster.get')
    def serverClustersGet(self, request):
        """ Get a Server Cluster """
        logging.info("serverClustersGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerClusterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerClusterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerClusterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        serverClustersController = ServerClustersController()

        if not request.key_id:
            return ServerClusterResponse(response_message="key_id is required")

        entity = serverClustersController.get_by_key_id(int(request.key_id))

        response = ServerClusterResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            gameKeyId = entity.gameKeyId,
            max_count = entity.max_count,
            min_online = entity.min_online,
            serverCreationMode = entity.serverCreationMode,
            server_to_game_transfer_threshold = entity.server_to_game_transfer_threshold,
            game_to_server_initial_transfer_amount = entity.game_to_server_initial_transfer_amount,
            travelMode = entity.travelMode,
            newPlayerStartMode = entity.newPlayerStartMode,
            rejoiningPlayerStartMode = entity.rejoiningPlayerStartMode,

            server_manager_task = entity.server_manager_task_running,

            vm_project = entity.vm_project,
            vm_bucket = entity.vm_bucket,
            vm_region = entity.vm_region,
            vm_zone = entity.vm_zone,
            vm_disk_image = entity.vm_disk_image,
            vm_machine_type = entity.vm_machine_type,
            vm_startup_script_location = entity.vm_startup_script_location,
            vm_shutdown_script_location = entity.vm_shutdown_script_location,

            accept_matchmaker_events_for_this_region = entity.accept_matchmaker_events_for_this_region,

            response_message='Success.',
            response_successful=True
        )

        return response

    @endpoints.method(SERVER_CLUSTER_EDIT_RESOURCE, ServerClusterResponse, path='serverClusterUpdate', http_method='POST', name='cluster.update')
    def serverClusterupdate(self, request):
        """ Update a server cluster - restricted to developer - PROTECTED """
        logging.info("serverClusterupdate")

        serverClusterController = ServerClustersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerClusterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerClusterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerClusterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerClusterResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        try:
            servercluster = serverClusterController.get_by_key_id(request.key_id)
            if not servercluster:
                return ServerClusterResponse(response_message='Error: cluster not found by specified key', response_successful=False)

        except:
            logging.info('servercluster not found.  aborting')
            return ServerClusterResponse(response_message='Error: servercluster not found by specified key', response_successful=False)

        ## deal with starting/stopping the server manager task
        if request.server_manager_task != servercluster.server_manager_task_running:
            logging.info('server manager task has changed')

            if request.server_manager_task:
                logging.info('attempting to start the server manager task')
                servercluster.server_manager_task_should_stop = False

                taskUrl='/task/game/servercluster/shardmanager'
                taskqueue.add(url=taskUrl, queue_name='taskServerManager', params={'key_id': servercluster.key.id()
                                                                                    }, countdown=2)

            else:
                logging.info('attempting to stop the server manager task')
                servercluster.server_manager_task_should_stop = True

        servercluster.title = request.title
        servercluster.description = request.description
        servercluster.max_count = request.max_count
        servercluster.min_online = request.min_online
        #servercluster.gameKeyId = request.gameKeyId
        servercluster.groupCluster = request.groupCluster
        servercluster.groupKeyId = request.groupKeyId
        servercluster.groupTitle = request.groupTitle

        servercluster.serverCreationMode = request.serverCreationMode
        servercluster.server_to_game_transfer_threshold = request.server_to_game_transfer_threshold
        servercluster.game_to_server_initial_transfer_amount = request.game_to_server_initial_transfer_amount
        servercluster.travelMode = request.travelMode

        servercluster.newPlayerStartMode = request.newPlayerStartMode
        servercluster.rejoiningPlayerStartMode = request.rejoiningPlayerStartMode

        servercluster.server_manager_task_running = request.server_manager_task

        servercluster.vm_project = request.vm_project
        servercluster.vm_bucket = request.vm_bucket
        servercluster.vm_region = request.vm_region
        servercluster.vm_zone = region_zone_mapper(request.vm_region)
        servercluster.vm_disk_image = request.vm_disk_image
        servercluster.vm_machine_type = request.vm_machine_type
        servercluster.vm_startup_script_location = request.vm_startup_script_location
        servercluster.vm_shutdown_script_location = request.vm_shutdown_script_location

        servercluster.accept_matchmaker_events_for_this_region = request.accept_matchmaker_events_for_this_region

        ## TODO - if these VM settings have changed, we are going to need to go through and update all of the child servers

        serverClusterController.update(servercluster)

        ## update firebase
        taskUrl='/task/servercluster/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': servercluster.key.id(), 'gameKeyId': servercluster.gameKeyId }, countdown = 2,)

        return ServerClusterResponse(key_id = servercluster.key.id(),
                response_message='servercluster Updated.', response_successful=True
                )

    @endpoints.method(SERVER_CLUSTER_EDIT_RESOURCE, ServerClusterResponse, path='serverClusterClone', http_method='POST', name='cluster.clone')
    def serverClusterClone(self, request):
        """ Clone a server cluster - restricted to developer - PROTECTED """
        logging.info("serverClusterClone")

        serverClusterController = ServerClustersController()
        serversController = ServersController()
        serverLinksController = ServerLinksController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerClusterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerClusterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerClusterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerClusterResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        try:
            servercluster = serverClusterController.get_by_key_id(request.key_id)
            if not servercluster:
                return ServerClusterResponse(response_message='Error: cluster not found by specified key', response_successful=False)

        except:
            logging.info('servercluster not found.  aborting')
            return ServerClusterResponse(response_message='Error: servercluster not found by specified key', response_successful=False)

        ## ok...
        ## get all of the servers in the selected cluster
        ## Create a new cluster
        ## create a new server set, and empty out the balances
        ## Do the server links while looping through

        server_cluster_clone = serverClusterController.create(
            title = servercluster.title + "-Clone",
            description = servercluster.description,
            max_count = servercluster.max_count,
            min_online = servercluster.min_online,
            gameKeyId = servercluster.gameKeyId,
            groupCluster = servercluster.groupCluster,
            groupKeyId = servercluster.groupKeyId,
            groupTitle = servercluster.groupTitle,
            userKeyId = servercluster.userKeyId,
            userTitle = servercluster.userTitle,
            serverCreationMode = servercluster.serverCreationMode,
            server_to_game_transfer_threshold = servercluster.server_to_game_transfer_threshold,
            game_to_server_initial_transfer_amount = servercluster.game_to_server_initial_transfer_amount,
            travelMode = servercluster.travelMode,
            newPlayerStartMode = servercluster.newPlayerStartMode,
            rejoiningPlayerStartMode = servercluster.rejoiningPlayerStartMode,
            server_manager_task_running = False,
            vm_project = servercluster.vm_project,
            vm_bucket = servercluster.vm_bucket,
            vm_region = servercluster.vm_region,
            vm_zone = servercluster.vm_zone,
            vm_disk_image = servercluster.vm_disk_image,
            vm_machine_type = servercluster.vm_machine_type,
            vm_startup_script_location = servercluster.vm_startup_script_location,
            vm_shutdown_script_location = servercluster.vm_shutdown_script_location
        )

        ## get servers from the original
        curs = Cursor()

        logging.info('looking up servers by serverClusterKeyId ')
        entities, cursor, more = serversController.list_page_not_instanced_sharded_by_serverClusterKeyId(int(servercluster.key.id()), start_cursor=curs)

        ## keep track of the newly created servers in a list.  WE need them in the same order for later
        server_clone_list = []

        for server in entities:
            logging.info("found a server - cloning")


            server_clone = serversController.create(
                title = server.title,
                description = server.description,
                hostAddress = "",
                hostPort = "",
                hostConnectionLink = "",
                gameKeyId = server.gameKeyId,
                gameTitle = server.gameTitle,
                userKeyId = server.userKeyId,
                minimumCurrencyHold = server.minimumCurrencyHold,
                totalCurrencyHeld = 0,
                incrementCurrency = server.incrementCurrency,
                currencyAwarded = 0,
                apiKey = serversController.create_unique_api_key(),
                apiSecret = serversController.key_generator(),
                continuous_server_provisioned = False,
                continuous_server_entry = True,
                continuous_server_creating = False,
                continuous_server_active = False,
                serverInfoRefreshNeeded = False,
                invisible = False,
                invisible_developer_setting = False,
                admissionFee = server.admissionFee,
                serverClusterKeyId = server_cluster_clone.key.id(),
                session_host_address = "",
                session_id = "",
                infinite_server_unused = server.infinite_server_unused,
                gameLevelKeyId = server.gameLevelKeyId,
                gameLevelTitle = server.gameLevelTitle,
                server_to_game_transfer_threshold = server.server_to_game_transfer_threshold,
                travelMode = server.travelMode,
                randomRef = server.randomRef,
                serverCurrency = 0,
                requireBadgeTags = server.requireBadgeTags,
                bannerServingUrl = server.bannerServingUrl,
                continuous_server = server.continuous_server,
                instance_server_template = server.instance_server_template,
                instance_server_purge_after_use = server.instance_server_purge_after_use,
                instance_server_purge_delay_seconds = server.instance_server_purge_delay_seconds,
                instance_server_configuration = server.instance_server_configuration,
                instance_party_size_maximum = server.instance_party_size_maximum,
                sharded_server_template = server.sharded_server_template,
                shard_count_maximum = server.shard_count_maximum,
                sharded_player_capacity_threshold = server.sharded_player_capacity_threshold,
                sharded_player_capacity_maximum = server.sharded_player_capacity_maximum,
                vendors_allowed = server.vendors_allowed,
                player_created_vendors_allowed = server.player_created_vendors_allowed,
                configuration = server.configuration,
                drop_items_permitted = server.drop_items_permitted,
                pickup_items_permitted = server.pickup_items_permitted
            )

            taskUrl='/task/server/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_clone.key.id()}, countdown = 7,)

            server_clone_list.append(server_clone)

            ## set up the chat channel
            server_chat_title = server.title + " chat"
            chat_channel = ChatChannelsController().create(
                title = server_chat_title,
                #text_enabled = True,
                #data_enabled = False,
                channel_type = 'server',
                adminUserKeyId = authorized_user.key.id(),
                refKeyId = server_clone.key.id(),
                gameKeyId = server_clone.gameKeyId,
                max_subscribers = 200
            )

        logging.info("Finished creating servers")

        ## Also get and create all of the server links from this server.
        ## Wait, we need both servers for links...  In this create server for loop, the target destination might not exist...
        ## Instead, we need to keep a copy of the new servers in the same order as the old servers so we can get the matching key from the index

        for i, server in enumerate(entities):
            logging.info("found a server - looking for links")

            server_links, cursor, more = serverLinksController.list_page_by_userKeyId_originServerKeyId(server.userKeyId, server.key.id(), start_cursor=curs)

            for server_link in server_links:
                logging.info("found a server link to clone.")

                target_server_index = self.get_matching_server_index(entities, server_link.targetServerKeyId)

                if target_server_index:
                    logging.info("found the target server")

                    server_link_clone = serverLinksController.create(
                        originServerKeyId = server_clone_list[i].key.id(),
                        originServerTitle = server_clone_list[i].title,
                        serverClusterKeyId = servercluster.key.id(),
                        serverClusterTitle = servercluster.title,
                        targetServerKeyId = server_clone_list[target_server_index].key.id(),
                        targetServerTitle = server_clone_list[target_server_index].title,
                        targetStatusIsContinuous = server_clone_list[target_server_index].continuous_server,
                        targetStatusProvisioned = server_clone_list[target_server_index].continuous_server_provisioned,
                        targetStatusOnline = server_clone_list[target_server_index].continuous_server_active,
                        targetStatusCreating = server_clone_list[target_server_index].continuous_server_creating,
                        targetStatusFull = False,
                        targetStatusDead = False,
                        permissionCanMount = server_link.permissionCanMount,
                        permissionCanUserTravel = server_link.permissionCanUserTravel,
                        permissionCanDismount = server_link.permissionCanDismount,
                        isEntryPoint = server_link.isEntryPoint,
                        userKeyId = server_link.userKeyId,
                        resourcesUsedToTravel = server_link.resourcesUsedToTravel,
                        resourceAmountsUsedToTravel = server_link.resourceAmountsUsedToTravel,
                        currencyCostToTravel = server_link.currencyCostToTravel,
                        coordLocationX = server_link.coordLocationX,
                        coordLocationY = server_link.coordLocationY,
                        coordLocationZ = server_link.coordLocationZ,
                        destinationLocationX = server_link.destinationLocationX,
                        destinationLocationY = server_link.destinationLocationY,
                        destinationLocationZ = server_link.destinationLocationZ,
                        rotationX = server_link.rotationX,
                        rotationY = server_link.rotationY,
                        rotationZ = server_link.rotationZ,
                        gameKeyId = server_link.gameKeyId,
                        targetInstanced = server_link.targetInstanced,
                        targetInstanceConfiguration = server_link.targetInstanceConfiguration,
                        targetInstancePartySizeMaximum = server_link.targetInstancePartySizeMaximum
                    )


        ## update firebase
        taskUrl='/task/servercluster/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_cluster_clone.key.id(), 'gameKeyId': server_cluster_clone.gameKeyId }, countdown = 2,)


        return ServerClusterResponse(key_id = servercluster.key.id(),
                response_message='servercluster Cloned.', response_successful=True
                )

    def get_matching_server_index(self, server_list, serverKeyId):
        """ get matching server """
        for i, server in enumerate(server_list):
            if server.key.id() == serverKeyId:
                logging.info('found match')
                return i
        return None

    @endpoints.method(SERVER_CLUSTER_EDIT_RESOURCE, ServerClusterResponse, path='serverClusterDelete', http_method='POST', name='cluster.delete')
    def serverClusterDelete(self, request):
        """ Delete a server cluster - restricted to developer - PROTECTED """
        logging.info("serverClusterDelete")

        serverController = ServersController()
        serverClusterController = ServerClustersController()
        serverLinksController = ServerLinksController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerClusterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerClusterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerClusterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerClusterResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        try:
            servercluster = serverClusterController.get_by_key_id(request.key_id)
            if not servercluster:
                return ServerClusterResponse(response_message='Error: cluster not found by specified key', response_successful=False)

        except:
            logging.info('servercluster not found.  aborting')
            return ServerClusterResponse(response_message='Error: servercluster not found by specified key', response_successful=False)

        ## don't allow delete if the server manager task is running
        if servercluster.server_manager_task_running:
            logging.info('server manager task is running - denying')
            return ServerClusterResponse(key_id = servercluster.key.id(),
                    response_message='servercluster NOT Deleted.  Manager Task is running.  Stop it first. ', response_successful=False
                    )


        ## deal with all of the servers and server links.
        logging.info('looking up servers by serverClusterKeyId ')
        curs = Cursor()
        entities, cursor, more = serverController.list_page_not_instanced_sharded_by_serverClusterKeyId(int(servercluster.key.id()), start_cursor=curs)

        for server in entities:
            logging.info('found a server to delete')
            if server.continuous_server_provisioned:
                logging.info('server is provisioned -aborting')
                return ServerClusterResponse(key_id = servercluster.key.id(),
                     response_message='servercluster NOT Deleted.  One or more servers is propvisioned. ', response_successful=False
                     )

            if server.continuous_server_creating:
                logging.info('server is creating -aborting')
                return ServerClusterResponse(key_id = servercluster.key.id(),
                        response_message='servercluster NOT Deleted.  One or more servers is creating. ', response_successful=False
                        )

            if server.serverCurrency < 0:
                logging.info('server balance is below zero -aborting')
                return ServerClusterResponse(key_id = servercluster.key.id(),
                        response_message='servercluster NOT Deleted.  One or more servers has a negative balance. ', response_successful=False
                        )

        logging.info('servers look ok to delete')

        for server in entities:
            logging.info('found a server to delete')
            ## todo deal with balances and such

            ## get the server links associated with this.

            server_links, cursor, more = serverLinksController.list_page_by_userKeyId_originServerKeyId(server.userKeyId, server.key.id(), start_cursor=curs)

            for server_link in server_links:
                logging.info("found a server link to delete.")

                serverLinksController.delete(server_link)

            serverController.delete(server)

        ## update firebase - this will cause a deletion
        taskUrl='/task/servercluster/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': servercluster.key.id(), 'gameKeyId': servercluster.gameKeyId }, countdown = 2,)

        serverClusterController.delete(servercluster)

        return ServerClusterResponse(key_id = servercluster.key.id(),
                response_message='servercluster Updated.', response_successful=True
                )

    @endpoints.method(SERVER_CLUSTER_COLLECTION_PAGE_RESOURCE, ServerClusterCollection, path='serverClusterCollectionGetPage', http_method='POST', name='cluster.collection.get.page')
    def serverClusterCollectionGetPage(self, request):
        """ Get a collection of server clusters """
        logging.info("serverClusterCollectionGetPage")

        serverClusterController = ServerClustersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerClusterCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerClusterCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerClusterCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()
        sort_order = request.sort_order
        direction = request.direction

        logging.info(request.gameKeyId)

        if request.gameKeyId:
            logging.info('listing by gameKeyId')
            server_clusters, cursor, more = serverClusterController.list_page_by_gameKeyId(request.gameKeyId,start_cursor=curs, order=sort_order)

        if request.gameKeyIdStr:
            logging.info('listing by gameKeyIdStr')
            server_clusters, cursor, more = serverClusterController.list_page_by_gameKeyId(int(request.gameKeyIdStr),start_cursor=curs, order=sort_order)
        #else:
        #    server_clusters, cursor, more = serverClusterController.list_page_by_gameKeyId(authorized_user.key.id(), start_cursor=curs, order=sort_order)

        server_cluster_list = []

        for server_cluster in server_clusters:
            server_cluster_list.append(ServerClusterResponse(
                key_id = server_cluster.key.id(),
                key_id_str = str(server_cluster.key.id()),
                title = server_cluster.title,
                description = server_cluster.description,
                max_count = server_cluster.max_count,
                min_online = server_cluster.min_online,
                gameKeyId = server_cluster.gameKeyId,
                groupCluster = server_cluster.groupCluster,
                groupKeyId = server_cluster.groupKeyId,
                groupTitle = server_cluster.groupTitle,
                userKeyId = server_cluster.userKeyId,
                userTitle = server_cluster.userTitle,
                serverCreationMode = server_cluster.serverCreationMode,
                server_to_game_transfer_threshold = server_cluster.server_to_game_transfer_threshold,
                game_to_server_initial_transfer_amount = server_cluster.game_to_server_initial_transfer_amount,
                travelMode = server_cluster.travelMode
            ))

        logging.info(len(server_cluster_list))

        if cursor:
            cursor_urlsafe = cursor.urlsafe()
        else:
            cursor_urlsafe = None

        response = ServerClusterCollection(
            server_clusters = server_cluster_list,
            more = more,
            cursor = cursor_urlsafe,
        )

        return response

    ##################
    ## Server Links
    ##################

    @endpoints.method(SERVER_LINK_CREATE_RESOURCE, ServerLinkResponse, path='serverLinkCreate', http_method='POST', name='link.create')
    def serverLinkCreate(self, request):
        """ Create a server link - restricted to developer - PROTECTED """
        logging.info("serverLinkCreate")

        serverController = ServersController()
        serverClusterController = ServerClustersController()
        serverLinksController = ServerLinksController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerLinkResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        if request.targetServerKeyId == request.originServerKeyId:
            return ServerLinkResponse(response_message='Error: Cannot link a server to itself', response_successful=False)

        server_cluster = serverClusterController.get_by_key_id(request.serverClusterKeyId)
        if not server_cluster:
            return ServerLinkResponse(response_message='Error: Server links must be associated with a server cluster', response_successful=False)

        target_server = serverController.get_by_key_id(request.targetServerKeyId)
        if not target_server:
            return ServerLinkResponse(response_message='Error: Could not find the target server with the supplied key', response_successful=False)

        origin_server = serverController.get_by_key_id(request.originServerKeyId)
        if not origin_server:
            return ServerLinkResponse(response_message='Error: Could not find the origin server with the supplied key', response_successful=False)

        ## TODO check to see if there are already max links in this cluster

        ## check to see if this link already exists
        existing_server_link = serverLinksController.get_by_originServerKeyId_targetServerKeyId(origin_server.key.id(), target_server.key.id())
        if existing_server_link:
            return ServerLinkResponse(response_message='Error: This server link already exists.', response_successful=False)

        serverLink = serverLinksController.create(
            originServerKeyId = origin_server.key.id(),
            originServerTitle = origin_server.title,
            serverClusterKeyId = server_cluster.key.id(),
            serverClusterTitle = server_cluster.title,
            targetServerKeyId = target_server.key.id(),
            targetServerTitle = target_server.title,
            targetStatusIsContinuous = target_server.continuous_server,
            targetStatusProvisioned = target_server.continuous_server_provisioned,
            targetStatusOnline = target_server.continuous_server_active,
            targetStatusCreating = target_server.continuous_server_creating,
            targetStatusFull = False,
            targetStatusDead = False,
            permissionCanMount = request.permissionCanMount,
            permissionCanUserTravel = request.permissionCanUserTravel,
            permissionCanDismount = request.permissionCanDismount,
            isEntryPoint = request.isEntryPoint,
            userKeyId = authorized_user.key.id(),
            resourcesUsedToTravel = request.resourcesUsedToTravel,
            resourceAmountsUsedToTravel = request.resourceAmountsUsedToTravel,
            currencyCostToTravel = request.currencyCostToTravel,
            coordLocationX = request.coordLocationX,
            coordLocationY = request.coordLocationY,
            coordLocationZ = request.coordLocationZ,
            destinationLocationX = request.destinationLocationX,
            destinationLocationY = request.destinationLocationY,
            destinationLocationZ = request.destinationLocationZ,
            rotationX = request.rotationX,
            rotationY = request.rotationY,
            rotationZ = request.rotationZ,
            gameKeyId = origin_server.gameKeyId,
            targetInstanced = target_server.instance_server_template or False,
            targetInstanceConfiguration = target_server.instance_server_configuration or 'none',
            targetInstancePartySizeMaximum = target_server.instance_party_size_maximum or 0
        )


        return ServerLinkResponse(
                        key_id = serverLink.key.id(),
                        response_message = "Success.  Server link Created.", response_successful=True
                        )

    @endpoints.method(SERVER_LINK_EDIT_RESOURCE, ServerLinkResponse, path='serverLinkGet', http_method='POST', name='link.get')
    def serverLinkGet(self, request):
        """ Get a server link """
        logging.info("serverLinkGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        serverLinksController = ServerLinksController()

        if not request.key_id:
            return ServerLinkResponse(response_message="key_id is required")

        entity = serverLinksController.get_by_key_id(int(request.key_id))

        response = ServerLinkResponse(
            key_id = entity.key.id(),
            targetServerTitle = entity.targetServerTitle,
            gameKeyId = entity.gameKeyId,
            response_message='Success.',
            response_successful=True,
            permissionCanMount = entity.permissionCanMount,
            permissionCanUserTravel = entity.permissionCanUserTravel,
            permissionCanDismount = entity.permissionCanDismount,
            isEntryPoint = entity.isEntryPoint,
            resourcesUsedToTravel = entity.resourcesUsedToTravel,
            resourceAmountsUsedToTravel = entity.resourceAmountsUsedToTravel,
            currencyCostToTravel = entity.currencyCostToTravel,
            coordLocationX = entity.coordLocationX,
            coordLocationY = entity.coordLocationY,
            coordLocationZ = entity.coordLocationZ,
            rotationX = entity.rotationX,
            rotationY = entity.rotationY,
            rotationZ = entity.rotationZ,
            originServerTitle = entity.originServerTitle,
            serverClusterTitle = entity.serverClusterTitle,
            destinationLocationX = entity.destinationLocationX,
            destinationLocationY = entity.destinationLocationY,
            destinationLocationZ = entity.destinationLocationZ,
            targetStatusCreating = entity.targetStatusCreating,
            targetStatusProvisioned = entity.targetStatusProvisioned,
            targetStatusOnline = entity.targetStatusOnline
        )

        return response

    @endpoints.method(SERVER_LINK_EDIT_RESOURCE, ServerLinkResponse, path='serverLinkUpdate', http_method='POST', name='link.update')
    def serverLinkUpdate(self, request):
        """ Update a server link - PROTECTED """
        logging.info("serverLinkUpdate")

        serverClusterController = ServerClustersController()
        serverLinksController = ServerLinksController()
        serverController = ServersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerLinkResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        serverLink = serverLinksController.get_by_key_id(request.key_id)
        if not serverLink:
            return ServerLinkResponse(response_message='Error: Could not find the server link with the supplied key.', response_successful=False)

        target_server = serverController.get_by_key_id(serverLink.targetServerKeyId)
        if not target_server:
            return ServerLinkResponse(response_message='Error: Could not find the target server with the supplied key', response_successful=False)

        if serverLink.userKeyId != authorized_user.key.id():
            logging.info('user key mismatch')
            return ServerLinkResponse(response_message='Error: Cannot update a link that you do not own.', response_successful=False)


        serverLink.permissionCanMount = request.permissionCanMount
        serverLink.permissionCanUserTravel = request.permissionCanUserTravel
        serverLink.permissionCanDismount = request.permissionCanDismount
        serverLink.isEntryPoint = request.isEntryPoint

        serverLink.resourcesUsedToTravel = request.resourcesUsedToTravel
        serverLink.resourceAmountsUsedToTravel = request.resourceAmountsUsedToTravel
        serverLink.currencyCostToTravel = request.currencyCostToTravel

        serverLink.coordLocationX = request.coordLocationX
        serverLink.coordLocationY = request.coordLocationY
        serverLink.coordLocationZ = request.coordLocationZ

        serverLink.rotationX = request.rotationX
        serverLink.rotationY = request.rotationY
        serverLink.rotationZ = request.rotationZ

        ## update instance stuff too - set defaults so that the json is still valid
        serverLink.targetInstanced = target_server.instance_server_template or False
        serverLink.targetInstanceConfiguration = target_server.instance_server_configuration or 'none'
        serverLink.targetInstancePartySizeMaximum = target_server.instance_party_size_maximum or 0

        serverLink.destinationLocationX = request.destinationLocationX
        serverLink.destinationLocationY = request.destinationLocationY
        serverLink.destinationLocationZ = request.destinationLocationZ

        serverLink.targetStatusCreating = request.targetStatusCreating
        serverLink.targetStatusProvisioned = request.targetStatusProvisioned
        serverLink.targetStatusOnline = request.targetStatusOnline

        serverLinksController.update(serverLink)

        return ServerLinkResponse(key_id = serverLink.key.id(),
                response_message='serverlink Updated.', response_successful=True
                )

    @endpoints.method(SERVER_LINK_EDIT_RESOURCE, ServerLinkResponse, path='serverLinkDelete', http_method='POST', name='link.delete')
    def serverLinkDelete(self, request):
        """ Delete a server link - PROTECTED """
        logging.info("serverLinkDelete")

        serverClusterController = ServerClustersController()
        serverLinksController = ServerLinksController()
        serverController = ServersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return ServerLinkResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        serverLink = serverLinksController.get_by_key_id(request.key_id)
        if not serverLink:
            return ServerLinkResponse(response_message='Error: Could not find the server link with the supplied key.', response_successful=False)

        if serverLink.userKeyId != authorized_user.key.id():
            logging.info('user key mismatch')
            return ServerLinkResponse(response_message='Error: Cannot delete a link that you do not own.', response_successful=False)

        serverLinksController.delete(serverLink)

        return ServerLinkResponse(response_message='Success:  Server link deleted. ', response_successful=True)



    @endpoints.method(SERVER_LINK_COLLECTION_PAGE_RESOURCE, ServerLinkCollection, path='serverLinkCollectionGetPage', http_method='POST', name='link.collection.get.page')
    def serverLinkCollectionGetPage(self, request):
        """ Get a collection of server links """
        logging.info("serverLinkCollectionGetPage")

        serverLinksController = ServerLinksController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerLinkCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerLinkCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerLinkCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        sort_order = request.sort_order
        direction = request.direction

        logging.info(authorized_user.key.id())
        logging.info(request.originServerKeyId)

        server_links, cursor, more = serverLinksController.list_page_by_userKeyId_originServerKeyId(authorized_user.key.id(), request.originServerKeyId, start_cursor=curs)
        server_link_list = []

        for server_link in server_links:
            server_link_list.append(ServerLinkResponse(
                key_id = server_link.key.id(),
                originServerKeyId = server_link.originServerKeyId,
                permissionCanMount = server_link.permissionCanMount,
                permissionCanUserTravel = server_link.permissionCanUserTravel,
                permissionCanDismount = server_link.permissionCanDismount,
                isEntryPoint = server_link.isEntryPoint,
                serverClusterKeyId = server_link.serverClusterKeyId,
                targetServerKeyId = server_link.targetServerKeyId,
                targetServerTitle = server_link.targetServerTitle,
                gameKeyId = server_link.gameKeyId
            ))

        if cursor:
            cursor_urlsafe = cursor.urlsafe()
        else:
            cursor_urlsafe = None

        response = ServerLinkCollection(
            server_links = server_link_list,
            more = more,
            cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(SERVER_PLAYER_RESOURCE, ServerPlayerResponse, path='serverPlayerGet', http_method='POST', name='player.get')
    def serverPlayerGet(self, request):
        """ Get a server player """
        logging.info("serverPlayerGet")

        userController = UsersController()
        serverController = ServersController()
        serverPlayerController = ServerPlayersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ServerPlayerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ServerPlayerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ServerPlayerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the server
        server = serverController.get_by_key_id(int(request.key_id))
        if not server:
            return ServerPlayerResponse(response_message='Error: server not found with the supplied key', response_successful=False)

        server_player = serverPlayerController.get_server_user(server.key.id(), authorized_user.key.id())
        if not server_player:
            return ServerPlayerResponse(response_message='Error:  Server Player Not Found.', response_successful=False)
        else:
            return ServerPlayerResponse(
                    key_id = server_player.key.id(),
                    currencyCurrent = server_player.currencyCurrent,
                    currencyEarned = server_player.currencyEarned,
                    pending_authorize = server_player.pending_authorize,
                    pending_deauthorize = server_player.pending_deauthorize,
                    authorized = server_player.authorized,
                    active = server_player.active,
                    banned = server_player.banned,
                    online = server_player.online,
                    ladderRank = server_player.ladderRank,
                    admission_paid = server_player.admission_paid,
                    experience = server_player.experience,
                    experience_total = server_player.experience_total,
                    serverClusterKeyId = server.serverClusterKeyId,
                    response_message='Success.',
                    response_successful=True)
