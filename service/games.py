import endpoints
import logging
import uuid
import urllib
import json
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
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

##from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.models.games import Games, GamesResponse, GAME_CREATE_RESOURCE, GAMES_RESOURCE, GamesCollection, GAMES_COLLECTION_PAGE_RESOURCE
from apps.uetopia.models.game_players import *
from apps.uetopia.models.game_player_snapshot import *
from apps.uetopia.models.game_modes import *
from apps.uetopia.models.game_levels import *
from apps.uetopia.models.game_level_links import *
from apps.uetopia.models.game_data import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_player_snapshot import GamePlayerSnapshotController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_levels import GameLevelsController
from apps.uetopia.controllers.game_level_links import GameLevelLinksController
from apps.uetopia.controllers.game_data import GameDataController

from apps.uetopia.controllers.server_clusters import ServerClustersController

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController

from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController

from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController

from apps.uetopia.utilities.server_parallel_template_detect_init import detect_init_parallel_server
from apps.uetopia.utilities.server_shard_detect_init import detect_init_shard_server

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="games", version="v1", description="Games API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class GamesApi(remote.Service):
    @endpoints.method(GAME_CREATE_RESOURCE, GamesResponse, path='create', http_method='POST', name='create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def create(self, request):
        """ Create a game - PROTECTED """
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GamesResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()

        #if games.from_datastore:
        #    raise endpoints.BadRequestException()
        gController.create(
            description = request.description,
            title = request.title,
            userKeyId = authorized_user.key.id(),
            apiKey = gController.create_unique_api_key(),
            apiSecret = gController.key_generator(),
            partySizeMaximum = 8,
            trustable = True,
            invisible=True,
            invisible_developer_setting = True,
            match_timeout_max_minutes = 60
            ## TODO other game init values
            )


        return GamesResponse(response_message="Game Created")

    @endpoints.method(GAMES_COLLECTION_PAGE_RESOURCE, GamesCollection, path='gamesCollectionGetPage', http_method='POST', name='collection.get.page')
    def gamesCollectionGetPage(self, request):
        """ Get a collection of games """
        logging.info("gamesCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gamesController = GamesController()

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        sort_order = request.sort_order
        direction = request.direction

        if authorized_user.admin:
            entities = gamesController.list()
        else:
            #entities, cursor, more = gamesController.list_page(start_cursor=curs)
            entities = gamesController.get_visible_dev()

        entity_list = []

        for entity in entities:
            entity_list.append(GamesResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description
            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = GamesCollection(
            games = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(message_types.VoidMessage, GamesCollection, path='gamesCollectionDeveloperGetPage', http_method='POST', name='collection.developer.get.page')
    def gamesCollectionDeveloperGetPage(self, request):
        """ Get a collection of games for a developer """
        logging.info("gamesCollectionDeveloperGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesCollection(response_message='Error: No User Record Found. ', response_successful=False)

        gamesController = GamesController()

        entities = gamesController.get_by_userKeyId(authorized_user.key.id())
        entity_list = []

        for entity in entities:
            entity_list.append(GamesResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                banner_url = entity.banner_url,
                icon_url = entity.icon_url
            ))

        response = GamesCollection(
            games = entity_list
        )

        return response


    @endpoints.method(GAMES_RESOURCE, GamesResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a single game """
        logging.info("gamesGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gamesController = GamesController()
        groupGameController = GroupGamesController()

        if request.key_id:
            entity = gamesController.get_by_key_id(int(request.key_id))

        elif request.groupGameKeyId:
            logging.info('getting through group key')

            group_game = groupGameController.get_by_key_id(request.groupGameKeyId)
            if not group_game:
                logging.info('no group game record found')
                return GamesResponse(response_message='Error: No Group Game Record Found. ', response_successful=False)

            entity = gamesController.get_by_key_id(group_game.gameKeyId)

        else:
            return GamesResponse(response_message="key_id or groupGameKeyId are required")

        if authorized_user.admin:
            ## send all the admin data
            response = GamesResponse(
                key_id = entity.key.id(),
                title = entity.title,
                userKeyId = entity.userKeyId,
                description = entity.description,
                instructions = entity.instructions,
                apiKey = entity.apiKey,
                apiSecret = entity.apiSecret,
                genre = entity.genre,
                download_url = entity.download_url,
                website_url = entity.website_url,
                icon_url = entity.icon_url,
                banner_url = entity.banner_url,
                css_url = entity.css_url,
                supported = entity.supported,
                invisible = entity.invisible,
                invisible_developer_setting = entity.invisible_developer_setting,
                approved = entity.approved,
                openToAllDevelopers = entity.openToAllDevelopers,
                server_instace_match_deploy = entity.server_instace_match_deploy,
                server_instance_continuous = entity.server_instance_continuous,
                tournaments_allowed = entity.tournaments_allowed,
                #vendors_allowed = entity.vendors_allowed,
                player_configuration_titles = entity.player_configuration_titles,
                player_configuration_ids = entity.player_configuration_ids,
                show_number_of_players = entity.show_number_of_players,
                game_join_link_base = entity.game_join_link_base,
                order = entity.order,
                partySizeMaximum = entity.partySizeMaximum,
                trustable = entity.trustable,
                usersCanCreateServers = entity.usersCanCreateServers,
                groupsCanCreateServers = entity.groupsCanCreateServers,
                characters_enabled = entity.characters_enabled,
                character_slots_new_user_default = entity.character_slots_new_user_default or 1,

                match_deploy_vm = entity.match_deploy_vm,
                match_deploy_vm_project = entity.match_deploy_vm_project,
                match_deploy_vm_bucket = entity.match_deploy_vm_bucket,
                match_deploy_vm_source_disk_image = entity.match_deploy_vm_source_disk_image,
                match_deploy_vm_machine_type = entity.match_deploy_vm_machine_type,
                match_deploy_vm_startup_script_location = entity.match_deploy_vm_startup_script_location,
                match_deploy_vm_shutdown_script_location = entity.match_deploy_vm_shutdown_script_location,
                match_deploy_vm_local_testing = entity.match_deploy_vm_local_testing,
                match_deploy_vm_local_testing_connection_string = entity.match_deploy_vm_local_testing_connection_string,
                match_deploy_vm_local_APIKey = entity.match_deploy_vm_local_APIKey,
                match_deploy_vm_local_APISecret = entity.match_deploy_vm_local_APISecret,

                match_allow_metagame = entity.match_allow_metagame,
                match_metagame_api_url = entity.match_metagame_api_url,

                match_timeout_max_minutes = entity.match_timeout_max_minutes,

                slack_webhook = entity.slack_webhook,
                slack_subscribe_vm_activity = entity.slack_subscribe_vm_activity,
                slack_subscribe_errors = entity.slack_subscribe_errors,
                slack_subscribe_transactions = entity.slack_subscribe_transactions,
                slack_subscribe_config_changes = entity.slack_subscribe_config_changes,
                slack_subscribe_new_players = entity.slack_subscribe_new_players,
                slack_subscribe_new_tournaments = entity.slack_subscribe_new_tournaments,
                slack_subscribe_tournament_rounds = entity.slack_subscribe_tournament_rounds,

                discord_webhook = entity.discord_webhook,
                discord_webhook_admin = entity.discord_webhook_admin,
                discord_subscribe_vm_activity = entity.discord_subscribe_vm_activity,
                discord_subscribe_errors = entity.discord_subscribe_errors,
                discord_subscribe_transactions = entity.discord_subscribe_transactions,
                discord_subscribe_config_changes = entity.discord_subscribe_config_changes,
                discord_subscribe_new_players = entity.discord_subscribe_new_players,
                discord_subscribe_new_tournaments = entity.discord_subscribe_new_tournaments,
                discord_subscribe_tournament_rounds = entity.discord_subscribe_tournament_rounds,
                discord_subscribe_match_win = entity.discord_subscribe_match_win,

                discord_subscribe_matchmaker_task_status = entity.discord_subscribe_matchmaker_task_status,
                discord_subscribe_server_manager_status = entity.discord_subscribe_server_manager_status,

                discord_webhook_na_northeast1 = entity.discord_webhook_na_northeast1,
                discord_webhook_us_central1 = entity.discord_webhook_us_central1,
                discord_webhook_us_west1 = entity.discord_webhook_us_west1,
                discord_webhook_us_west2 = entity.discord_webhook_us_west2,
                discord_webhook_us_west3 = entity.discord_webhook_us_west3,
                discord_webhook_us_west4 = entity.discord_webhook_us_west4,
                discord_webhook_us_east4 = entity.discord_webhook_us_east4,
                discord_webhook_us_east1 = entity.discord_webhook_us_east1,
                discord_webhook_southamerica_east1 = entity.discord_webhook_southamerica_east1,
                discord_webhook_europe_north1 = entity.discord_webhook_europe_north1,
                discord_webhook_europe_west1 = entity.discord_webhook_europe_west1,
                discord_webhook_europe_west2 = entity.discord_webhook_europe_west2,
                discord_webhook_europe_west3 = entity.discord_webhook_europe_west3,
                discord_webhook_europe_west4 = entity.discord_webhook_europe_west4,
                discord_webhook_europe_west6 = entity.discord_webhook_europe_west6,
                discord_webhook_asia_south1 = entity.discord_webhook_asia_south1,
                discord_webhook_asia_southeast1 = entity.discord_webhook_asia_southeast1,
                discord_webhook_asia_east1 = entity.discord_webhook_asia_east1,
                discord_webhook_asia_east2 = entity.discord_webhook_asia_east2,
                discord_webhook_asia_northeast1 = entity.discord_webhook_asia_northeast1,
                discord_webhook_asia_northeast2 = entity.discord_webhook_asia_northeast2,
                discord_webhook_asia_northeast3 = entity.discord_webhook_asia_northeast3,
                discord_webhook_australia_southeast1 = entity.discord_webhook_australia_southeast1,

                group_custom_texture_instructions_link = entity.group_custom_texture_instructions_link,
                group_custom_texture_default = entity.group_custom_texture_default,

                enforce_locks = entity.enforce_locks,
                #vendorDataTableId = entity.vendorDataTableId,

                patcher_enabled = entity.patcher_enabled,
                patcher_details_xml = entity.patcher_details_xml,

                response_message='Success.',
                response_successful=True
            )

        elif entity.userKeyId == authorized_user.key.id():
            ## send all of the developer data
            response = GamesResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                instructions = entity.instructions,
                apiKey = entity.apiKey,
                apiSecret = entity.apiSecret,
                download_url = entity.download_url,
                website_url = entity.website_url,
                icon_url = entity.icon_url,
                banner_url = entity.banner_url,
                css_url = entity.css_url,
                invisible_developer_setting = entity.invisible_developer_setting,
                genre = entity.genre,
                partySizeMaximum = entity.partySizeMaximum,
                #download_url = entity.download_url,
                usersCanCreateServers = entity.usersCanCreateServers,
                groupsCanCreateServers = entity.groupsCanCreateServers,

                server_instace_match_deploy = entity.server_instace_match_deploy,
                server_instance_continuous = entity.server_instance_continuous,
                tournaments_allowed = entity.tournaments_allowed,
                #vendors_allowed = entity.vendors_allowed,
                characters_enabled = entity.characters_enabled,
                character_slots_new_user_default = entity.character_slots_new_user_default or 1,

                match_deploy_vm = entity.match_deploy_vm,
                match_deploy_vm_project = entity.match_deploy_vm_project,
                match_deploy_vm_bucket = entity.match_deploy_vm_bucket,
                match_deploy_vm_source_disk_image = entity.match_deploy_vm_source_disk_image,
                match_deploy_vm_machine_type = entity.match_deploy_vm_machine_type,
                match_deploy_vm_startup_script_location = entity.match_deploy_vm_startup_script_location,
                match_deploy_vm_shutdown_script_location = entity.match_deploy_vm_shutdown_script_location,

                match_deploy_vm_local_testing = entity.match_deploy_vm_local_testing,
                match_deploy_vm_local_testing_connection_string = entity.match_deploy_vm_local_testing_connection_string,
                match_deploy_vm_local_APIKey = entity.match_deploy_vm_local_APIKey,
                match_deploy_vm_local_APISecret = entity.match_deploy_vm_local_APISecret,

                match_allow_metagame = entity.match_allow_metagame,
                match_metagame_api_url = entity.match_metagame_api_url,

                match_timeout_max_minutes = entity.match_timeout_max_minutes,

                slack_webhook = entity.slack_webhook,
                slack_subscribe_vm_activity = entity.slack_subscribe_vm_activity,
                slack_subscribe_errors = entity.slack_subscribe_errors,
                slack_subscribe_transactions = entity.slack_subscribe_transactions,
                slack_subscribe_config_changes = entity.slack_subscribe_config_changes,
                slack_subscribe_new_players = entity.slack_subscribe_new_players,
                slack_subscribe_new_tournaments = entity.slack_subscribe_new_tournaments,
                slack_subscribe_tournament_rounds = entity.slack_subscribe_tournament_rounds,

                discord_webhook = entity.discord_webhook,
                discord_webhook_admin = entity.discord_webhook_admin,
                discord_subscribe_vm_activity = entity.discord_subscribe_vm_activity,
                discord_subscribe_errors = entity.discord_subscribe_errors,
                discord_subscribe_transactions = entity.discord_subscribe_transactions,
                discord_subscribe_config_changes = entity.discord_subscribe_config_changes,
                discord_subscribe_new_players = entity.discord_subscribe_new_players,
                discord_subscribe_new_tournaments = entity.discord_subscribe_new_tournaments,
                discord_subscribe_tournament_rounds = entity.discord_subscribe_tournament_rounds,
                discord_subscribe_match_win = entity.discord_subscribe_match_win,

                discord_subscribe_matchmaker_task_status = entity.discord_subscribe_matchmaker_task_status,
                discord_subscribe_server_manager_status = entity.discord_subscribe_server_manager_status,

                discord_webhook_na_northeast1 = entity.discord_webhook_na_northeast1,
                discord_webhook_us_central1 = entity.discord_webhook_us_central1,
                discord_webhook_us_west1 = entity.discord_webhook_us_west1,
                discord_webhook_us_west2 = entity.discord_webhook_us_west2,
                discord_webhook_us_west3 = entity.discord_webhook_us_west3,
                discord_webhook_us_west4 = entity.discord_webhook_us_west4,
                discord_webhook_us_east4 = entity.discord_webhook_us_east4,
                discord_webhook_us_east1 = entity.discord_webhook_us_east1,
                discord_webhook_southamerica_east1 = entity.discord_webhook_southamerica_east1,
                discord_webhook_europe_north1 = entity.discord_webhook_europe_north1,
                discord_webhook_europe_west1 = entity.discord_webhook_europe_west1,
                discord_webhook_europe_west2 = entity.discord_webhook_europe_west2,
                discord_webhook_europe_west3 = entity.discord_webhook_europe_west3,
                discord_webhook_europe_west4 = entity.discord_webhook_europe_west4,
                discord_webhook_europe_west6 = entity.discord_webhook_europe_west6,
                discord_webhook_asia_south1 = entity.discord_webhook_asia_south1,
                discord_webhook_asia_southeast1 = entity.discord_webhook_asia_southeast1,
                discord_webhook_asia_east1 = entity.discord_webhook_asia_east1,
                discord_webhook_asia_east2 = entity.discord_webhook_asia_east2,
                discord_webhook_asia_northeast1 = entity.discord_webhook_asia_northeast1,
                discord_webhook_asia_northeast2 = entity.discord_webhook_asia_northeast2,
                discord_webhook_asia_northeast3 = entity.discord_webhook_asia_northeast3,
                discord_webhook_australia_southeast1 = entity.discord_webhook_australia_southeast1,

                group_custom_texture_instructions_link = entity.group_custom_texture_instructions_link,
                group_custom_texture_default = entity.group_custom_texture_default,

                enforce_locks = entity.enforce_locks,
                #vendorDataTableId = entity.vendorDataTableId,
                patcher_enabled = entity.patcher_enabled,
                patcher_details_xml = entity.patcher_details_xml,

                response_message='Success.',
                response_successful=True
            )
        else:
            ## send only the public data
            response = GamesResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                instructions = entity.instructions,
                icon_url = entity.icon_url,
                banner_url = entity.banner_url,
                genre = entity.genre,
                download_url = entity.download_url,
                usersCanCreateServers = entity.usersCanCreateServers,
                groupsCanCreateServers = entity.groupsCanCreateServers,
                response_message='Success.',
                response_successful=True
            )

        return response

    @endpoints.method(GAMES_RESOURCE, GamesResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update a game - PROTECTED """
        logging.info("gamesUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GamesResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gamesController = GamesController()

        if not request.key_id:
            return GamesResponse(response_message="key_id is required", response_successful=False)

        entity = gamesController.get_by_key_id(int(request.key_id))

        if not entity:
            logging.error("Error: No game found with the supplied key_id")
            return GamesResponse(response_message="Error: No game found with the supplied key_id", response_successful=False)

        dirty = False

        ## if the name has changed, fire off a task to handle the renaming
        if entity.title != request.title:
            logging.info('firing off a task to do renaming')

            taskUrl='/task/game/rename'
            taskqueue.add(url=taskUrl, queue_name='gameRename', params={'key_id': entity.key.id()}, countdown = 2,)

        ## make sure the duration maximum is within limits
        match_timeout_max_minutes = 60
        if request.match_timeout_max_minutes:
            if request.match_timeout_max_minutes < 10:
                logging.info('request.match_timeout_max_minutes was less than 10')
                match_timeout_max_minutes = 10
            if request.match_timeout_max_minutes > 240:
                logging.info('request.match_timeout_max_minutes was greater than 240')
                match_timeout_max_minutes = 240

        ## keep track of the case that the max player count has changed so we can send a discord message as a warning
        game_max_player_count_changed = False

        if request.adminRequest:
            logging.info('performing admin update')
            if authorized_user.admin:
                logging.info('admin found')

                dirty = True
                ## update all the admin data

                logging.info(request.title)
                logging.info(request.description)

                entity.title = request.title
                entity.description = request.description
                entity.instructions = request.instructions
                entity.genre = request.genre
                entity.download_url = request.download_url

                entity.website_url = request.website_url
                entity.icon_url = request.icon_url
                entity.banner_url = request.banner_url
                entity.css_url = request.css_url
                entity.supported = request.supported
                entity.invisible = request.invisible
                entity.invisible_developer_setting = request.invisible_developer_setting
                entity.approved = request.approved
                entity.openToAllDevelopers = request.openToAllDevelopers
                entity.server_instace_match_deploy = request.server_instace_match_deploy
                entity.server_instance_continuous = request.server_instance_continuous
                entity.tournaments_allowed = request.tournaments_allowed
                #entity.vendors_allowed = request.vendors_allowed
                entity.characters_enabled = request.characters_enabled
                entity.character_slots_new_user_default = request.character_slots_new_user_default

                entity.match_deploy_vm = request.match_deploy_vm
                entity.match_deploy_vm_project = request.match_deploy_vm_project
                entity.match_deploy_vm_bucket = request.match_deploy_vm_bucket
                entity.match_deploy_vm_source_disk_image = request.match_deploy_vm_source_disk_image
                entity.match_deploy_vm_machine_type = request.match_deploy_vm_machine_type
                entity.match_deploy_vm_startup_script_location = request.match_deploy_vm_startup_script_location
                entity.match_deploy_vm_shutdown_script_location = request.match_deploy_vm_shutdown_script_location

                entity.match_deploy_vm_local_testing = request.match_deploy_vm_local_testing
                entity.match_deploy_vm_local_testing_connection_string = request.match_deploy_vm_local_testing_connection_string
                entity.match_deploy_vm_local_APIKey = request.match_deploy_vm_local_APIKey
                entity.match_deploy_vm_local_APISecret = request.match_deploy_vm_local_APISecret

                entity.match_allow_metagame = request.match_allow_metagame
                entity.match_metagame_api_url = request.match_metagame_api_url

                entity.match_timeout_max_minutes = match_timeout_max_minutes

                entity.game_join_link_base = request.game_join_link_base
                entity.order = request.order
                entity.partySizeMaximum = request.partySizeMaximum
                entity.trustable = request.trustable

                entity.slack_webhook = request.slack_webhook
                entity.slack_subscribe_vm_activity = request.slack_subscribe_vm_activity
                entity.slack_subscribe_errors = request.slack_subscribe_errors
                entity.slack_subscribe_transactions = request.slack_subscribe_transactions
                entity.slack_subscribe_config_changes = request.slack_subscribe_config_changes
                entity.slack_subscribe_new_players = request.slack_subscribe_new_players
                entity.slack_subscribe_new_tournaments = request.slack_subscribe_new_tournaments
                entity.slack_subscribe_tournament_rounds = request.slack_subscribe_tournament_rounds

                entity.discord_webhook = request.discord_webhook
                entity.discord_webhook_admin = request.discord_webhook_admin
                entity.discord_subscribe_vm_activity = request.discord_subscribe_vm_activity
                entity.discord_subscribe_errors = request.discord_subscribe_errors
                entity.discord_subscribe_transactions = request.discord_subscribe_transactions
                entity.discord_subscribe_config_changes = request.discord_subscribe_config_changes
                entity.discord_subscribe_new_players = request.discord_subscribe_new_players
                entity.discord_subscribe_new_tournaments = request.discord_subscribe_new_tournaments
                entity.discord_subscribe_tournament_rounds = request.discord_subscribe_tournament_rounds
                entity.discord_subscribe_match_win = request.discord_subscribe_match_win

                entity.usersCanCreateServers = request.usersCanCreateServers
                entity.groupsCanCreateServers = request.groupsCanCreateServers

                entity.group_custom_texture_instructions_link = request.group_custom_texture_instructions_link
                entity.group_custom_texture_default = request.group_custom_texture_default

                entity.enforce_locks = request.enforce_locks

                entity.patcher_enabled = request.patcher_enabled
                entity.patcher_details_xml = request.patcher_details_xml

                #entity.vendorDataTableId = request.vendorDataTableId

        else:
            logging.info('performing developer update')
            if entity.userKeyId == authorized_user.key.id():
                logging.info('owner found')

                if entity.character_slots_new_user_default != request.character_slots_new_user_default:
                    logging.info('character count max changed')
                    game_max_player_count_changed = True

                dirty = True
                ## update all of the developer data

                entity.title = request.title
                entity.description = request.description
                entity.instructions = request.instructions
                entity.genre = request.genre
                entity.download_url = request.download_url

                entity.website_url = request.website_url
                entity.icon_url = request.icon_url
                entity.banner_url = request.banner_url
                entity.css_url = request.css_url
                entity.invisible_developer_setting = request.invisible_developer_setting

                entity.partySizeMaximum = request.partySizeMaximum

                entity.usersCanCreateServers = request.usersCanCreateServers
                entity.groupsCanCreateServers = request.groupsCanCreateServers

                entity.server_instace_match_deploy = request.server_instace_match_deploy
                entity.server_instance_continuous = request.server_instance_continuous
                entity.tournaments_allowed = request.tournaments_allowed
                #entity.vendors_allowed = request.vendors_allowed
                entity.characters_enabled = request.characters_enabled
                entity.character_slots_new_user_default = request.character_slots_new_user_default

                entity.match_deploy_vm = request.match_deploy_vm
                entity.match_deploy_vm_project = request.match_deploy_vm_project
                entity.match_deploy_vm_bucket = request.match_deploy_vm_bucket
                entity.match_deploy_vm_source_disk_image = request.match_deploy_vm_source_disk_image
                entity.match_deploy_vm_machine_type = request.match_deploy_vm_machine_type
                entity.match_deploy_vm_startup_script_location = request.match_deploy_vm_startup_script_location
                entity.match_deploy_vm_shutdown_script_location = request.match_deploy_vm_shutdown_script_location

                entity.match_deploy_vm_local_testing = request.match_deploy_vm_local_testing
                entity.match_deploy_vm_local_testing_connection_string = request.match_deploy_vm_local_testing_connection_string
                entity.match_deploy_vm_local_APIKey = request.match_deploy_vm_local_APIKey
                entity.match_deploy_vm_local_APISecret = request.match_deploy_vm_local_APISecret

                entity.match_allow_metagame = request.match_allow_metagame
                entity.match_metagame_api_url = request.match_metagame_api_url

                entity.match_timeout_max_minutes = match_timeout_max_minutes

                entity.slack_webhook = request.slack_webhook
                entity.slack_subscribe_vm_activity = request.slack_subscribe_vm_activity
                entity.slack_subscribe_errors = request.slack_subscribe_errors
                entity.slack_subscribe_transactions = request.slack_subscribe_transactions
                entity.slack_subscribe_config_changes = request.slack_subscribe_config_changes
                entity.slack_subscribe_new_players = request.slack_subscribe_new_players
                entity.slack_subscribe_new_tournaments = request.slack_subscribe_new_tournaments
                entity.slack_subscribe_tournament_rounds = request.slack_subscribe_tournament_rounds

                entity.discord_webhook = request.discord_webhook
                entity.discord_webhook_admin = request.discord_webhook_admin
                entity.discord_subscribe_vm_activity = request.discord_subscribe_vm_activity
                entity.discord_subscribe_errors = request.discord_subscribe_errors
                entity.discord_subscribe_transactions = request.discord_subscribe_transactions
                entity.discord_subscribe_config_changes = request.discord_subscribe_config_changes
                entity.discord_subscribe_new_players = request.discord_subscribe_new_players
                entity.discord_subscribe_new_tournaments = request.discord_subscribe_new_tournaments
                entity.discord_subscribe_tournament_rounds = request.discord_subscribe_tournament_rounds
                entity.discord_subscribe_match_win = request.discord_subscribe_match_win

                entity.discord_subscribe_matchmaker_task_status = request.discord_subscribe_matchmaker_task_status
                entity.discord_subscribe_server_manager_status = request.discord_subscribe_server_manager_status

                entity.discord_webhook_na_northeast1 = request.discord_webhook_na_northeast1
                entity.discord_webhook_us_central1 = request.discord_webhook_us_central1
                entity.discord_webhook_us_west1 = request.discord_webhook_us_west1
                entity.discord_webhook_us_west2 = request.discord_webhook_us_west2
                entity.discord_webhook_us_west3 = request.discord_webhook_us_west3
                entity.discord_webhook_us_west4 = request.discord_webhook_us_west4
                entity.discord_webhook_us_east4 = request.discord_webhook_us_east4
                entity.discord_webhook_us_east1 = request.discord_webhook_us_east1
                entity.discord_webhook_southamerica_east1 = request.discord_webhook_southamerica_east1
                entity.discord_webhook_europe_north1 = request.discord_webhook_europe_north1
                entity.discord_webhook_europe_west1 = request.discord_webhook_europe_west1
                entity.discord_webhook_europe_west2 = request.discord_webhook_europe_west2
                entity.discord_webhook_europe_west3 = request.discord_webhook_europe_west3
                entity.discord_webhook_europe_west4 = request.discord_webhook_europe_west4
                entity.discord_webhook_europe_west6 = request.discord_webhook_europe_west6
                entity.discord_webhook_asia_south1 = request.discord_webhook_asia_south1
                entity.discord_webhook_asia_southeast1 = request.discord_webhook_asia_southeast1
                entity.discord_webhook_asia_east1 = request.discord_webhook_asia_east1
                entity.discord_webhook_asia_east2 = request.discord_webhook_asia_east2
                entity.discord_webhook_asia_northeast1 = request.discord_webhook_asia_northeast1
                entity.discord_webhook_asia_northeast2 = request.discord_webhook_asia_northeast2
                entity.discord_webhook_asia_northeast3 = request.discord_webhook_asia_northeast3
                entity.discord_webhook_australia_southeast1 = request.discord_webhook_australia_southeast1

                entity.group_custom_texture_instructions_link = request.group_custom_texture_instructions_link
                entity.group_custom_texture_default = request.group_custom_texture_default

                entity.enforce_locks = request.enforce_locks
                #entity.vendorDataTableId = request.vendorDataTableId
                entity.patcher_enabled = request.patcher_enabled
                entity.patcher_details_xml = request.patcher_details_xml

        if dirty:
            gamesController.update(entity)

            #if not entity.invisible:
            taskUrl='/task/game/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': entity.key.id()}, countdown = 2,)

            try:
                name = claims['name']
            except:
                name = claims['email']

            ## do slack/discord pushes if enabled
            if entity.slack_subscribe_config_changes and entity.slack_webhook:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Configuration Changed by: %s | %s" % (name, claims['email'])
                slack_data = {'text': message}
                data=json.dumps(slack_data)
                resp, content = http_auth.request(entity.slack_webhook,
                                  "POST",
                                  data,
                                  headers=headers)

            if entity.discord_subscribe_config_changes and entity.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Configuration Changed by: %s | %s" % (name, claims['email'])
                discord_data = { "embeds": [{"title": "Configuration Changed", "url": "https://example.com", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(entity.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)

            if game_max_player_count_changed:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Warning: the new player character maximum count has changed.  This new maximum will only apply to new players.  To change existing players maximum, use the developer interface. "
                discord_data = { "embeds": [{"title": "Character Max Count Warning", "url": "https://example.com", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(entity.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)


        response = GamesResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            genre = entity.genre,
            response_message='Success.  Game updated.',
            response_successful=True
        )

        return response

    @endpoints.method(GAMES_RESOURCE, GamesResponse, path='delete', http_method='POST', name='delete')
    def delete(self, request):
        """ Delete a game - PROTECTED """
        logging.info("gamesDelete")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GamesResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gamesController = GamesController()

        if not request.key_id:
            return GamesResponse(response_message="key_id is required", response_successful=False)

        entity = gamesController.get_by_key_id(int(request.key_id))



        if entity:
            ## only admins can do this.
            if authorized_user.admin:

                ## There's a ton of stuff to delete and process - moving this to a task instead.

                taskUrl='/task/game/delete'
                taskqueue.add(url=taskUrl, queue_name='gameDelete', params={'key_id': entity.key.id()}, countdown = 2,)

                return GamesResponse(response_message='Success.  Game deletion task started.', response_successful=True)
            else:

                admin_url = "https://ue4topia.appspot.com/#/admin/games/" + str(entity.key.id())

                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Game deletion requested by: %s | %s" % (authorized_user.title, claims['email'])
                discord_data = { "embeds": [{"title": "Game Deletion Requested", "url": admin_url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(DISCORD_WEBHOOK_ADMIN,
                                  "POST",
                                  data,
                                  headers=headers)

                return GamesResponse(response_message='Site admins have been notified and will delete this game soon.', response_successful=False)
        else:
            return GamesResponse(response_message='Error: Games not found.', response_successful=False)

    @endpoints.method(GAME_PLAYER_RESOURCE, GamePlayerResponse, path='gameClearMatches', http_method='POST', name='matches.clear')
    def gameClearMatches(self, request):
        """ Delete all of the game's matches and match related data - only the game owner can do this """
        logging.info("gameClearMatches")

        userController = UsersController()
        gameController = GamesController()
        matchController = MatchController()
        matchPlayerController = MatchPlayersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamePlayerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamePlayerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            return GamePlayerResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this is the admin for the game
        if authorized_user.key.id() != game.userKeyId:
            logging.info('Only the game owner can perform this action')
            return GamePlayerResponse(response_message='Error: Only the game owner can perform this action', response_successful=False)

        ## make sure the game is set to match_deploy_vm_local_testing
        if not game.match_deploy_vm_local_testing:
            logging.info('The game must be set to match local testing in order to perform this action')
            return GamePlayerResponse(response_message='Error: The game must be set to match local testing in order to perform this action', response_successful=False)

        ## TODO send a discord message

        ## get all of the matches
        game_matches = matchController.get_list_by_game(game.key.id())
        for match in game_matches:
            ## get the match players
            match_players = matchPlayerController.get_list_by_matchKeyId(match.key.id())
            for match_player in match_players:
                ## just delete it
                matchPlayerController.delete(match_player)
            ## delete the match too
            matchController.delete(match)

        return GamePlayerResponse(response_message='Success', response_successful=True)



    ######### GAME PLAYERS

    @endpoints.method(GAME_PLAYER_RESOURCE, GamePlayerResponse, path='gamePlayerUpdate', http_method='POST', name='player.update')
    def gamePlayerUpdate(self, request):
        """ Update a game player """
        logging.info("gamePlayerMemberUpdate")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        serverClusterController = ServerClustersController()

        teamController = TeamsController()
        teamMemberController = TeamMembersController()
        groupsController = GroupsController()
        #groupUsersController = GroupUsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamePlayerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamePlayerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            return GamePlayerResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## check for and execute developer request if flagged
        if request.developer:
            logging.info('developer request')
            if game.userKeyId != authorized_user.key.id():
                logging.info('developer mismatch')
                return GameCharacterCollection(response_message="You can only view characters in your games.", response_successful=False)

            game_player = gamePlayerController.get_by_key_id(request.gamePlayerKeyId)
            if not game_player:
                logging.info('no game player found with the supplied key')
                return GameCharacterCollection(response_message="no game player found with the supplied key.", response_successful=False)

            ## todo character count max

            ## update the game player with values from the dev form
            game_player.rank = request.rank
            game_player.score = request.score
            game_player.experience = request.experience
            game_player.experienceThisLevel = request.experienceThisLevel
            game_player.level = request.level
            game_player.inventory = request.inventory
            game_player.equipment = request.equipment
            game_player.abilities = request.abilities
            game_player.interface = request.interface
            game_player.crafting = request.crafting
            game_player.recipes = request.recipes
            game_player.character = request.character
            game_player.coordLocationX = request.coordLocationX
            game_player.coordLocationY = request.coordLocationY
            game_player.coordLocationZ = request.coordLocationZ
            game_player.zoneName = request.zoneName
            game_player.zoneKey = request.zoneKey
            game_player.lastServerKeyId = request.lastServerKeyId
            game_player.characterMaxAllowedCount = request.characterMaxAllowedCount

            ## do a discrord push for the game
            if game.discord_subscribe_config_changes and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Player: %s was manually changed" % (game_player.key.id())
                url = "http://ue4topia.appspot.com/#/developer/game/%s/players/%s" % (game.key.id(), game_player.key.id())
                discord_data = { "embeds": [{"title": "Player Data Changed", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)
            ## Save the player
            gamePlayerController.update(game_player)
            return GamePlayerResponse(response_message='Success.  Game Player Updated.', response_successful=True)



        ## make sure players have region set in profile
        if not authorized_user.region:
            if game.discord_subscribe_errors and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Error: %s attempted to setup for play, but they have not picked a region yet" % (authorized_user.title)
                url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)

            return GamePlayerResponse(response_message="Error: Where are you?  Please pick your region in your profile first!", response_successful=False)

        ## make sure the selected serverCluster is valid
        if request.lastServerClusterKeyId:
            lastServerClusterKeyId = int(request.lastServerClusterKeyId)
            selected_server_cluster = serverClusterController.get_by_key_id(lastServerClusterKeyId)
            if not selected_server_cluster:
                logging.info('server cluster not found')
                ## just assign one at random
                selected_server_cluster = serverClusterController.get_by_gameKeyId(game.key.id())
                lastServerClusterKeyId = selected_server_cluster.key.id()
                #return GamePlayerResponse(response_message="Error: The server cluster was not found", response_successful=False)
        else:
            logging.info('no server cluster chosen')
            ## just assign one at random
            selected_server_cluster = serverClusterController.get_by_gameKeyId(game.key.id())
            if selected_server_cluster:
                lastServerClusterKeyId = selected_server_cluster.key.id()
            else:
                logging.info('no server cluster could be assigned.')  # this could just be a matchmaker game that does not use clusters.
                lastServerClusterKeyId = None


        #logging.info('request.autoAuth: %s'%request.autoAuth)
        ## check if gpm exists
        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())
        if not game_player:
            showgameonprofile = False

            if request.showGameOnProfile:
                showgameonprofile = True

            game_player = gamePlayerController.create(
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                locked = False,
                online = True,
                rank = 1600,
                score = 0,
                #autoAuth = False,
                #autoAuthThreshold = 0,
                autoTransfer = request.autoTransfer,
                firebaseUser = authorized_user.firebaseUser,
                picture = authorized_user.picture,
                lastServerClusterKeyId = lastServerClusterKeyId,
                groupKeyId = authorized_user.groupTagKeyId,
                groupTag = authorized_user.groupTag,
                showGameOnProfile = showgameonprofile
            )

            ## do slack/discord pushes if enabled
            if game.slack_subscribe_config_changes and game.slack_webhook:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "New Player: %s | %s" % (authorized_user.key.id(), authorized_user.title)
                slack_data = {'text': message}
                data=json.dumps(slack_data)
                resp, content = http_auth.request(game.slack_webhook,
                                  "POST",
                                  data,
                                  headers=headers)

            if game.discord_subscribe_new_players and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "New Player: %s | %s" % (authorized_user.key.id(), authorized_user.title)
                url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                discord_data = { "embeds": [{"title": "New Player", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)
        else:
            ## game player exists

            game_player.lastServerClusterKeyId = lastServerClusterKeyId
            game_player.autoTransfer = request.autoTransfer

            game_player.groupKeyId = authorized_user.groupTagKeyId
            game_player.groupTag = authorized_user.groupTag

            if request.showGameOnProfile:
                game_player.showGameOnProfile = request.showGameOnProfile

            gamePlayerController.update(game_player)

        ## deal with the game chat channel

        taskUrl='/task/game/player/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game_player.key.id()}, countdown = 2,)


        ## check for trusted continuous games that have no entry point servers in operation - bring one up

        ## no more server creation on game player update/create

        gamePlayerController.update(game_player)

        return GamePlayerResponse(response_message='Success.  Game Player Updated.', response_successful=True)

    @endpoints.method(GAME_PLAYER_RESOURCE, GamePlayerResponse, path='attemptServerAllocate', http_method='POST', name='attempt.server.allocate')
    def attemptServerAllocate(self, request):
        """ Attempt to create the server for this player. """
        logging.info("attemptServerAllocate")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameCharacterController = GameCharactersController()
        serverClusterController = ServerClustersController()
        serverShardController = ServerShardsController()

        teamController = TeamsController()
        teamMemberController = TeamMembersController()
        groupsController = GroupsController()
        #groupUsersController = GroupUsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamePlayerResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamePlayerResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            logging.info('no game record found')
            return GamePlayerResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure players have region set in profile
        if not authorized_user.region:
            logging.info("Error: Where are youuuu?  Please pick your region in your profile first!")
            return GamePlayerResponse(response_message="Error: Where are youuuu?  Please pick your region in your profile first!", response_successful=False)


        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())
        if not game_player:
            logging.info('no game player record found')
            return GamePlayerResponse(response_message='Error: Game player not found with the supplied key.  Authorize on the website first!', response_successful=False)

        ## if the game uses characters, we need the active character
        if game.characters_enabled:
            logging.info('characters enabled')
            if game_player.characterCurrentKeyId:
                logging.info('found a characterCurrentKeyId')
                game_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
            else:
                logging.info('but there was no characterCurrentKeyId')
                game_character = None


        ## check for trusted continuous games that have no entry point servers in operation - bring one up

        error_occurred = False
        error_message = ""

        ## redoing this for the new mode logic.
        serverController = ServersController()
        serverClusterController = ServerClustersController()
        serverShardPlaceholderController = ServerShardPlaceholderController()

        if game.trustable:
            ## if it's not trustable servers are brought up using the server play dialog instead - each get authorized individually
            if game.server_instance_continuous:
                ## if its matchmaker they get created on the fly on a per-match basis
                logging.info('found a trusted game that uses continuous servers')

                ## handle allocation of specific server by key
                ## this is only allowed if travel mode is set to free
                if request.serverKeyIdStr:
                    logging.info('found serverKeyIdStr')

                    server_to_use = serverController.get_by_key_id(int(request.serverKeyIdStr))
                    server_cluster = serverClusterController.get_by_key_id(server_to_use.serverClusterKeyId)

                    ## make sure it exists - it could have errored out
                    if server_to_use:
                        if server_cluster.travelMode == "free":
                            logging.info("travelMode is free - allowing this server allocation process")

                            ## save the serverKey to the game player - TODO do we need this?
                            game_player.lastServerKeyId = server_to_use.key.id()

                            ## start a task to create the vm
                            taskUrl='/task/server/vm/allocate'
                            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                    "serverKeyId": server_to_use.key.id()
                                                                                                })
                            return GamePlayerResponse(response_message='Success.  Attempting to bring up a server', response_successful=True)

                        else:
                            logging.info('server cluster travel mode is not set to free.  Denied')
                            message = "Player %s attempted to allocate a server directly, but the cluster %s is not set to free travel, so the request was denied." % (game_player.userTitle, server_cluster.title)

                            if game.discord_subscribe_errors and game.discord_webhook_admin:
                                http_auth = Http()
                                headers = {"Content-Type": "application/json"}
                                discord_data = { "embeds": [{"title": "Server Allocate - Denied", "url": "https://example.com", "description": message}] }
                                data=json.dumps(discord_data)
                                resp, content = http_auth.request(game.discord_webhook_admin,
                                                  "POST",
                                                  data,
                                                  headers=headers)

                            return GamePlayerResponse(response_message=message, response_successful=False)


                ## If we are here, we are just looking to bring up ANY server.
                ## We might already have a pending placeholder for one.
                existing_placeholder = serverShardPlaceholderController.get_by_userKeyId_gameKeyId(game_player.userKeyId, game.key.id())

                if existing_placeholder:
                    logging.info('found an existing placeholder')

                    server_shard = serverShardController.get_by_key_id(existing_placeholder.serverShardKeyId)

                    if server_shard:
                        logging.info('found server shard record')

                        if not server_shard.online:
                            logging.info('it is not currently online.  Attempting to bring it up.')

                            ## start a task to create the vm
                            taskUrl='/task/server/vm/allocate'
                            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                    "serverKeyId": existing_placeholder.serverKeyId
                                                                                                })
                            return GamePlayerResponse(response_message='Success.  Attempting to bring up a server', response_successful=True)

                    ## if there is a placeholder but something else was wrong, abort
                    return GamePlayerResponse(response_message='Failure.  Found a placeholder, but there was an error retieving the shard', response_successful=False)


                ## get the user's team/party (if any)
                team = None
                team_member = teamMemberController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())
                if team_member:
                    team = teamController.get_by_key_id(team_member.teamKeyId)

                ## get the user's group (if any)
                group = None
                if authorized_user.groupTagKeyId:
                    group = groupsController.get_by_key_id(authorized_user.groupTagKeyId)


                ## is it a new player or returning player?
                if game_player.lastServerClusterKeyId:
                    logging.info('lastServerClusterKeyId exists')
                    server_cluster = serverClusterController.get_by_key_id(game_player.lastServerClusterKeyId)




                    if server_cluster.rejoiningPlayerStartMode == 'previous':
                        logging.info('cluster set to previous')

                        # get the previous location
                        previous_server = None
                        # if characters are enabled, use the character instead
                        if game.characters_enabled and game_character:
                            if game_character.lastServerKeyId:
                                logging.info('found game_character.lastServerKeyId')
                                previous_server = serverController.get_by_key_id(game_character.lastServerKeyId)
                        else:
                            # get the player's previous location
                            if game_player.lastServerKeyId:
                                logging.info('found game_player.lastServerKeyId')
                                previous_server = serverController.get_by_key_id(game_player.lastServerKeyId)

                        if not previous_server:
                            logging.info('previous server not found - reverting to random entry')

                            entry_server = serverController.get_random_entry_by_gameKeyId_serverClusterKeyId(game.key.id(), server_cluster.key.id())
                            if entry_server:
                                logging.info('found a server')

                                ## check for sharded server before checking provisioned
                                if entry_server.sharded_server_template:

                                    ## 3/18/20 Use the shard manager here to handle the allocation.
                                    server_to_use = detect_init_shard_server(entry_server, authorized_user, team, team_member)
                                else:
                                    server_to_use = entry_server

                                if not server_to_use.continuous_server_provisioned:
                                    logging.info('Its not already provisioned - bringing it up for play')

                                    ## check and handle parallel server mode
                                    if server_to_use.instance_server_template:
                                        server_to_use = detect_init_parallel_server(server_to_use, authorized_user, team, team_member, group)

                                    ## make sure it exists - it could have errored out
                                    if server_to_use:
                                        ## save the serverKey to the game player
                                        game_player.lastServerKeyId = server_to_use.key.id()

                                        ## start a task to create the vm
                                        taskUrl='/task/server/vm/allocate'
                                        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                                "serverKeyId": server_to_use.key.id()
                                                                                                            })
                                        """
                                        ## push an alert out to firebase
                                        taskUrl='/task/user/alert/create'
                                        description = "Bringing up an entry server for you. "
                                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                                                        'material_icon': MATERIAL_ICON_VM_CREATE,
                                                                                                        'importance': 'md-primary',
                                                                                                        ## TODO this message can be more helpful
                                                                                                        'message_text': description,
                                                                                                        #'action_button_color': 'primary',
                                                                                                        #'action_button_sref': '/profile'
                                                                                                        }, countdown = 0,)
                                        """



                        else:
                            logging.info('previous_server exists')
                            ## make sure the old server is in the cluster that the user just selected.
                            if previous_server.serverClusterKeyId == server_cluster.key.id():
                                logging.info('server cluster match')
                                ##  check to see if this is a shard
                                if previous_server.sharded_from_template:
                                    logging.info('sharded_from_template')
                                    ## get the server_shard record so we can check the player count
                                    server_shard = serverShardController.get_by_serverShardKeyId(previous_server.key.id())
                                    if not server_shard:
                                        logging.error('server shard record was not found')

                                    if server_shard.playerCount < server_shard.playerCapacityMaximum:
                                        logging.info('shard has room')

                                        if not previous_server.continuous_server_provisioned:
                                            ## start a task to create the vm
                                            taskUrl='/task/server/vm/allocate'
                                            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                                    "serverKeyId": previous_server.key.id()
                                                                                                                })
                                    else:
                                        logging.info('shard does not have room')

                                        ## get the shard template
                                        shard_server_template = serverController.get_by_key_id(previous_server.sharded_from_template_serverKeyId)
                                        if not shard_server_template:
                                            logging.error('shard_server_template not found')

                                        server_to_use = detect_init_shard_server(shard_server_template, authorized_user, team, team_member)

                                        if not server_to_use.continuous_server_provisioned:
                                            ## start a task to create the vm
                                            taskUrl='/task/server/vm/allocate'
                                            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                                    "serverKeyId": server_to_use.key.id()
                                                                                                                })

                                else:
                                    logging.info('this is not a sharded server - bringing it up')

                                    if not previous_server.continuous_server_provisioned:
                                        ## start a task to create the vm
                                        taskUrl='/task/server/vm/allocate'
                                        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                                "serverKeyId": previous_server.key.id()
                                                                                                            })


                            else:
                                logging.info('the user selected a different server cluster - reverting to random entry')
                                ## TODO copy over the user's previous location on this cluser if it exists.
                                entry_server = serverController.get_random_entry_by_gameKeyId_serverClusterKeyId(game.key.id(), server_cluster.key.id())
                                if entry_server:
                                    logging.info('found a server to bring up')

                                    ## check and handle parallel server mode
                                    if entry_server.instance_server_template:
                                        server_to_use = detect_init_parallel_server(entry_server, authorized_user, team, team_member, group)
                                    elif entry_server.sharded_server_template:
                                        server_to_use = detect_init_shard_server(entry_server, authorized_user, team, team_member)
                                    else:
                                        server_to_use = entry_server

                                    ## make sure it exists - it could have errored out
                                    if server_to_use:
                                        ## save the serverKey to the game player
                                        game_player.lastServerKeyId = server_to_use.key.id()

                                        ## start a task to create the vm
                                        taskUrl='/task/server/vm/allocate'
                                        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                                "serverKeyId": server_to_use.key.id()
                                                                                                            })
                                        ## push an alert out to firebase
                                        taskUrl='/task/user/alert/create'
                                        description = "Bringing up an entry server for you. "
                                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                                                        'material_icon': MATERIAL_ICON_VM_CREATE,
                                                                                                        'importance': 'md-primary',
                                                                                                        ## TODO this message can be more helpful
                                                                                                        'message_text': description,
                                                                                                        #'action_button_color': 'primary',
                                                                                                        #'action_button_sref': '/profile'
                                                                                                        }, countdown = 0,)

                    else:
                        logging.info('defaulting to random entry')
                        entry_server = serverController.get_random_entry_by_gameKeyId_serverClusterKeyId(game.key.id(), server_cluster.key.id())
                        if entry_server:
                            logging.info('found a server to bring up')

                            ## check and handle parallel server mode
                            if entry_server.instance_server_template:
                                server_to_use = detect_init_parallel_server(entry_server, authorized_user, team, team_member, group)
                            elif entry_server.sharded_server_template:
                                server_to_use = detect_init_shard_server(entry_server, authorized_user, team, team_member)
                            else:
                                server_to_use = entry_server

                            ## make sure it exists - it could have errored out
                            if server_to_use:
                                ## save the serverKey to the game player
                                game_player.lastServerKeyId = server_to_use.key.id()

                                ## start a task to create the vm
                                taskUrl='/task/server/vm/allocate'
                                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                        "serverKeyId": server_to_use.key.id()
                                                                                                    })
                                ## push an alert out to firebase
                                """
                                taskUrl='/task/user/alert/create'
                                description = "Bringing up an entry server for you. "
                                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                                                'material_icon': MATERIAL_ICON_VM_CREATE,
                                                                                                'importance': 'md-primary',
                                                                                                ## TODO this message can be more helpful
                                                                                                'message_text': description,
                                                                                                #'action_button_color': 'primary',
                                                                                                #'action_button_sref': '/profile'
                                                                                                }, countdown = 0,)
                                """

                else:
                    logging.info('new player')

                    ## TODO new player start modes
                    ## this is random entry
                    ## make sure a cluster was found:
                    if selected_server_cluster:
                        entry_server = serverController.get_random_entry_by_gameKeyId_serverClusterKeyId(game.key.id(), selected_server_cluster.key.id() )
                        if entry_server:
                            logging.info('found a server to bring up')

                            ## check and handle parallel server mode
                            if entry_server.instance_server_template:
                                server_to_use = detect_init_parallel_server(entry_server, authorized_user, team, team_member, group)
                            elif entry_server.sharded_server_template:
                                server_to_use = detect_init_shard_server(entry_server, authorized_user, team, team_member)
                            else:
                                server_to_use = entry_server

                            ## make sure it exists - it could have errored out
                            if server_to_use:

                                ## save the serverKey
                                if game.characters_enabled and game_character:
                                    # to the character
                                    game_character.lastServerKeyId = server_to_use.key.id()
                                else:
                                    #to the game player
                                    game_player.lastServerKeyId = server_to_use.key.id()

                                ## start a task to create the vm
                                taskUrl='/task/server/vm/allocate'
                                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                                        "serverKeyId": server_to_use.key.id()
                                                                                                    })
                                ## push an alert out to firebase
                                """
                                taskUrl='/task/user/alert/create'
                                description = "Bringing up an entry server for you. "
                                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                                                'material_icon': MATERIAL_ICON_VM_CREATE,
                                                                                                'importance': 'md-primary',
                                                                                                ## TODO this message can be more helpful
                                                                                                'message_text': description,
                                                                                                #'action_button_color': 'primary',
                                                                                                #'action_button_sref': '/profile'
                                                                                                }, countdown = 0,)
                                """

        if game.characters_enabled and game_character:
            gameCharacterController.update(game_character)
        else:
            gamePlayerController.update(game_player)

        if error_occurred:
            ## TODO slack discord game error
            ## TODO probably need to clear out the lastServerKeyId in this case too
            return GamePlayerResponse(response_message=error_message, response_successful=True)
        else:
            return GamePlayerResponse(response_message='Success.  Attempting to bring up a server', response_successful=True)


    @endpoints.method(GAME_PLAYER_COLLECTION_PAGE_RESOURCE, GamePlayersCollection, path='gamePlayerCollectionGetPage', http_method='POST', name='players.collection.developer.get.page')
    def gamePlayerCollectionGetPage(self, request):
        """ Get a collection of game players """
        logging.info("gamePlayersCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayersCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamePlayersCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamePlayersCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gameController = GamesController()
        gamePlayerController = GamePlayersController()


        ## grab the game
        ## allow lookup with a gameKey (gameKeyId)
        ## or a groupGameKeyId
        if request.gameKeyId:
            game = gameController.get_by_key_id(int(request.gameKeyId))
            if not game:
                logging.info('Game not found with the supplied key')
                return GamePlayersCollection(response_message='Error: Game not found with the supplied key', response_successful=False)
        else:
            logging.info('Supply a gameKeyId')
            return GamePlayersCollection(response_message='Error: Supply a gameKeyId', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GamePlayersCollection(response_message='Error: This is not your game.', response_successful=False)

        entities, cursor, more = gamePlayerController.list_by_gameKeyId_modified(request.gameKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(GamePlayerResponse(
                key_id = entity.key.id(),
                userTitle = entity.userTitle,
                created = entity.created.isoformat(),
                modified = entity.modified.isoformat()
            ))

        response = GamePlayersCollection(
            game_players = entity_list,
            response_successful=True
        )

        return response

    @endpoints.method(GAME_PLAYER_RESOURCE, GamePlayerResponse, path='gamePlayerGet', http_method='POST', name='player.get')
    def gamePlayerGet(self, request):
        """ Get a game player """
        logging.info("gamePlayerGet")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            logging.error('game not found')
            return GamePlayerResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## allow developer request
        if request.developer:
            logging.info('developer request')
            if game.userKeyId != authorized_user.key.id():
                logging.info('developer mismatch')
                return GameCharacterCollection(response_message="You can only view characters in your games.", response_successful=False)

            game_player = gamePlayerController.get_by_key_id(request.gamePlayerKeyId)

            if not game_player:
                logging.warning('game player not found')
                return GamePlayerResponse(response_message='Error:  Game Player Not Found.', response_successful=False, gameTrustable = game.trustable,)
            else:
                if game_player.gameKeyId != game.key.id():
                    logging.warning('game player gameKeyId mismatch ')
                    return GamePlayerResponse(response_message='Error:  game player gameKeyId mismatch', response_successful=False, gameTrustable = game.trustable,)

                ## developers get all info
                return GamePlayerResponse(
                        key_id = game_player.key.id(),
                        modified = game_player.modified.isoformat(),
                        rank = game_player.rank,
                        online = game_player.online,
                        userTitle = game_player.userTitle,
                        userKeyId = game_player.userKeyId,
                        #autoAuth = game_player.autoAuth,
                        #autoAuthThreshold = game_player.autoAuthThreshold,
                        autoTransfer = game_player.autoTransfer,
                        gameTrustable = game.trustable,
                        lastServerClusterKeyId = game_player.lastServerClusterKeyId,

                        locked = game_player.locked,
                        locked_by_serverKeyId = game_player.locked_by_serverKeyId,
                        score = game_player.score,
                        experience = game_player.experience,
                        experienceThisLevel = game_player.experienceThisLevel,
                        level = game_player.level,
                        inventory = game_player.inventory,
                        equipment = game_player.equipment,
                        abilities = game_player.abilities,
                        interface = game_player.interface,
                        crafting = game_player.crafting,
                        recipes = game_player.recipes,
                        character = game_player.character,
                        coordLocationX = game_player.coordLocationX,
                        coordLocationY = game_player.coordLocationY,
                        coordLocationZ = game_player.coordLocationZ,
                        zoneName = game_player.zoneName,
                        zoneKey = game_player.zoneKey,
                        lastServerKeyId = game_player.lastServerKeyId,
                        characterMaxAllowedCount = game_player.characterMaxAllowedCount,

                        response_message='Success.',
                        response_successful=True)
        else:
            logging.info('not developer request')

            game_player = gamePlayerController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())
            if not game_player:
                logging.warning('game player not found')
                return GamePlayerResponse(response_message='Error:  Game Player Not Found.', response_successful=False, gameTrustable = game.trustable,)
            else:
                return GamePlayerResponse(
                        key_id = game_player.key.id(),
                        rank = game_player.rank,
                        online = game_player.online,
                        #autoAuth = game_player.autoAuth,
                        #autoAuthThreshold = game_player.autoAuthThreshold,
                        autoTransfer = game_player.autoTransfer,
                        gameTrustable = game.trustable,
                        lastServerClusterKeyId = game_player.lastServerClusterKeyId,
                        response_message='Success.',
                        response_successful=True)

    ##get snapshot
    @endpoints.method(GAME_PLAYER_SNAPSHOT_RESOURCE, GamePlayerSnapshotResponse, path='gamePlayerSnapshotGet', http_method='POST', name='player.snapshot.get')
    def gamePlayerSnapshotGet(self, request):
        """ Get a game player snapshot """
        logging.info("gamePlayerSnapshotGet")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gamePlayerSnapshotController = GamePlayerSnapshotController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerSnapshotResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamePlayerSnapshotResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamePlayerSnapshotResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.gameKeyId))
        if not game:
            logging.error('game not found')
            return GamePlayerSnapshotResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## allow developer request
        if request.developerRequest:
            logging.info('developer request')
            if game.userKeyId != authorized_user.key.id():
                logging.info('developer mismatch')
                return GamePlayerSnapshotResponse(response_message="You can only view characters in your games.", response_successful=False)

            game_player_snapshot = gamePlayerSnapshotController.get_by_key_id(request.key_id)

            if not game_player_snapshot:
                logging.warning('game player snapshot not found')
                return GamePlayerSnapshotResponse(response_message='Error:  Game Player snapshot Not Found.', response_successful=False, gameTrustable = game.trustable,)
            else:
                if game_player_snapshot.gameKeyId != game.key.id():
                    logging.warning('game player snapshot gameKeyId mismatch ')
                    return GamePlayerSnapshotResponse(response_message='Error:  game player snapshot gameKeyId mismatch', response_successful=False, gameTrustable = game.trustable,)

                ## developers get all info
                return GamePlayerSnapshotResponse(
                        key_id = game_player_snapshot.key.id(),
                        created = game_player_snapshot.created.isoformat(),
                        rank = game_player_snapshot.rank,
                        online = game_player_snapshot.online,
                        userTitle = game_player_snapshot.userTitle,
                        userKeyId = game_player_snapshot.userKeyId,
                        #autoAuth = game_player.autoAuth,
                        #autoAuthThreshold = game_player.autoAuthThreshold,
                        lastServerClusterKeyId = game_player_snapshot.lastServerClusterKeyId,

                        characterRecord = game_player_snapshot.characterRecord,
                        characterKeyId = game_player_snapshot.characterKeyId,

                        player = game_player_snapshot.player,
                        gamePlayerKeyId = game_player_snapshot.gamePlayerKeyId,

                        score = game_player_snapshot.score,
                        experience = game_player_snapshot.experience,
                        experienceThisLevel = game_player_snapshot.experienceThisLevel,
                        level = game_player_snapshot.level,
                        inventory = game_player_snapshot.inventory,
                        equipment = game_player_snapshot.equipment,
                        abilities = game_player_snapshot.abilities,
                        interface = game_player_snapshot.interface,
                        crafting = game_player_snapshot.crafting,
                        recipes = game_player_snapshot.recipes,
                        character = game_player_snapshot.character,
                        coordLocationX = game_player_snapshot.coordLocationX,
                        coordLocationY = game_player_snapshot.coordLocationY,
                        coordLocationZ = game_player_snapshot.coordLocationZ,
                        zoneName = game_player_snapshot.zoneName,
                        zoneKey = game_player_snapshot.zoneKey,
                        lastServerKeyId = game_player_snapshot.lastServerKeyId,
                        title = game_player_snapshot.title,

                        response_message='Success.',
                        response_successful=True)
        else:
            logging.info('not developer request')

            logging.warning('non-developer requests are not implemented yet ')
            return GamePlayerSnapshotResponse(response_message='Error:  non-developer requests are not implemented yet ', response_successful=False, gameTrustable = game.trustable,)


            ## TODO - implement this if we need it.


    @endpoints.method(GAME_PLAYER_SNAPSHOT_COLLECTION_PAGE_RESOURCE, GamePlayerSnapshotCollection, path='gamePlayerSnapshotCollectionGetPage', http_method='POST', name='player.snapshot.collection.get.page')
    def gamePlayerSnapshotCollectionGetPage(self, request):
        """ Get a collection of game player snapshots """
        logging.info("gamePlayerSnapshotCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerSnapshotCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamePlayerSnapshotCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamePlayerSnapshotCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gamePlayerSnapshotController = GamePlayerSnapshotController()

        ## grab the game
        ## allow lookup with a gameKey (gameKeyId)
        ## or a groupGameKeyId
        if request.gameKeyId:
            game = gameController.get_by_key_id(int(request.gameKeyId))
            if not game:
                logging.info('Game not found with the supplied key')
                return GamePlayerSnapshotCollection(response_message='Error: Game not found with the supplied key', response_successful=False)
        else:

            logging.info('Supply a gameKeyId')
            return GamePlayerSnapshotCollection(response_message='Error: Supply a gameKeyId', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            logging.info('geveloper does not own this game')
            return GamePlayerSnapshotCollection(response_message='Error: This is not your game.', response_successful=False)

        ## Allow lookup by gamePlayerKeyId, or characterKeyId
        entity_list = []
        if request.characterKeyId:
            logging.info('found characterKeyId: %s' %request.characterKeyId)
            entities, cursor, more  = gamePlayerSnapshotController.get_list_by_characterKeyId(request.characterKeyId)
        else:
            logging.info('looking up by gamePlayerKeyId')
            entities, cursor, more  = gamePlayerSnapshotController.get_list_by_gamePlayerKeyId(request.gamePlayerKeyId)


        for entity in entities:
            logging.info('found snapshot')
            entity_list.append(GamePlayerSnapshotResponse(
                key_id = entity.key.id(),
                userTitle = entity.userTitle,
                created = entity.created.isoformat(),
                modified = entity.modified.isoformat()
            ))

        response = GamePlayerSnapshotCollection(
            snapshots = entity_list,
            response_successful=True
        )

        return response


    ##################### GAME MODES
    @endpoints.method(GAME_MODE_RESOURCE, GameModeResponse, path='gameModeCreate', http_method='POST', name='mode.create')
    def gameModeCreate(self, request):
        """ Create a game mode - PROTECTED """
        logging.info("gameModeCreate")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameModescontroller = GameModesController()

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameModeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameModeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameModeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        if not authorized_user:
            logging.info('no user record found')
            return GameModeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            return GameModeResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameModeResponse(response_message='Error: This is not your game.', response_successful=False)

        ## TODO any more checks?

        ## add the game mode
        game_mode = gameModescontroller.create(
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            onlineSubsystemReference = request.onlineSubsystemReference,

            playersPerTeam = request.playersPerTeam,
            teams = request.teams,
            admissionFeePerPlayer = request.admissionFeePerPlayer,
            winRewardPerPlayer = request.winRewardPerPlayer,
            matchmakerAlgorithm = request.matchmakerAlgorithm,
            matchmakerDisparityMax = request.matchmakerDisparityMax,
            requireBadgeTags = request.requireBadgeTags
        )

        return GameModeResponse(response_message='Success.', response_successful=True)


    @endpoints.method(GAME_MODES_COLLECTION_PAGE_RESOURCE, GameModesCollection, path='gameModesCollectionGetPage', http_method='POST', name='modes.collection.developer.get.page')
    def gameModesCollectionGetPage(self, request):
        """ Get a collection of game modes """
        logging.info("gameModesCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameModesCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameModesCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameModesCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gameModescontroller = GameModesController()
        gameController = GamesController()
        groupGameController = GroupGamesController()

        ## grab the game
        ## allow lookup with a gameKey (gameKeyId)
        ## or a groupGameKeyId
        if request.gameKeyId:
            game = gameController.get_by_key_id(int(request.gameKeyId))
            if not game:
                logging.info('Game not found with the supplied key')
                return GameModesCollection(response_message='Error: Game not found with the supplied key', response_successful=False)
        elif request.groupGameKeyId:
            group_game = groupGameController.get_by_key_id(request.groupGameKeyId)
            if not group_game:
                logging.info('Group Game Key found, but could not find the group_game record')
                return GameModesCollection(response_message='Error: Group Game Key found, but could not find the group_game record', response_successful=False)

            game = gameController.get_by_key_id(int(group_game.gameKeyId))
            if not game:
                logging.info('Game not found with the supplied key')
                return GameModesCollection(response_message='Error: Game not found with the supplied key', response_successful=False)
        else:
            logging.info('Supply a gameKeyId or groupGameKeyId')
            return GameModesCollection(response_message='Error: Supply a gameKeyId or groupGameKeyId', response_successful=False)

        ## make sure this user is the owner of the game
        ## muting this.  We need all players to be able to read this.
        #if not authorized_user.key.id() == game.userKeyId:
        #    return GameModesCollection(response_message='Error: This is not your game.', response_successful=False)

        entities = gameModescontroller.get_by_gameKeyId(request.gameKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(GameModeResponse(
                key_id = entity.key.id(),
                gameKeyId = entity.gameKeyId,
                gameTitle = entity.gameTitle,
                onlineSubsystemReference = entity.onlineSubsystemReference,
                playersPerTeam = entity.playersPerTeam,
                teams = entity.teams,
                admissionFeePerPlayer = entity.admissionFeePerPlayer,
                winRewardPerPlayer = entity.winRewardPerPlayer,
                ads_allowed = entity.ads_allowed,
                ads_require_approval = entity.ads_require_approval,
                ads_minimum_bid_per_impression = entity.ads_minimum_bid_per_impression,
                ads_description = entity.ads_description
            ))

        response = GameModesCollection(
            game_modes = entity_list,
            response_successful=True
        )

        return response

    @endpoints.method(GAME_MODE_RESOURCE, GameModeResponse, path='gameModeGet', http_method='POST', name='mode.get')
    def gameModeGet(self, request):
        """ Get a game mode """
        logging.info("gameModeGet")

        userController = UsersController()
        gameController = GamesController()
        gameModesController = GameModesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameModeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameModeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameModeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game mode
        gamemode = gameModesController.get_by_key_id(int(request.key_id))
        if not gamemode:
            return GameModeResponse(response_message='Error: Game Mode not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(gamemode.gameKeyId)
        if not game:
            return GameModeResponse(response_message='Error: Game not found', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameModeResponse(response_message='Error: This is not your game.', response_successful=False)



        return GameModeResponse(
                key_id = gamemode.key.id(),

                gameKeyId = gamemode.gameKeyId,
                gameTitle = gamemode.gameTitle,
                onlineSubsystemReference = gamemode.onlineSubsystemReference,
                playersPerTeam = gamemode.playersPerTeam,
                teams = gamemode.teams,
                admissionFeePerPlayer = gamemode.admissionFeePerPlayer,
                winRewardPerPlayer = gamemode.winRewardPerPlayer,

                matchmakerAlgorithm = gamemode.matchmakerAlgorithm,
                matchmakerDisparityMax = gamemode.matchmakerDisparityMax,

                ads_allowed = gamemode.ads_allowed,
                ads_require_approval = gamemode.ads_require_approval,
                ads_required = gamemode.ads_required,
                ads_default_textures = gamemode.ads_default_textures,
                ads_per_match_maximum = gamemode.ads_per_match_maximum,
                ads_minimum_bid_per_impression = gamemode.ads_minimum_bid_per_impression,
                ads_description = gamemode.ads_description,

                teamSizeMin = gamemode.teamSizeMin,
                teamSizeMax = gamemode.teamSizeMax,
                requireBadgeTags = gamemode.requireBadgeTags,

                response_message='Success.',
                response_successful=True)

    @endpoints.method(GAME_MODE_RESOURCE, GameModeResponse, path='gameModeUpdate', http_method='POST', name='mode.update')
    def gameModeUpdate(self, request):
        """ Update a game mode - PROTECTED """
        logging.info("gameModeUpdate")

        userController = UsersController()
        gameController = GamesController()
        gameModesController = GameModesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameModeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameModeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameModeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameModeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game mode
        gamemode = gameModesController.get_by_key_id(int(request.key_id))
        if not gamemode:
            return GameModeResponse(response_message='Error: Game Mode not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(gamemode.gameKeyId)
        if not game:
            return GameModeResponse(response_message='Error: Game not found', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameModeResponse(response_message='Error: This is not your game.', response_successful=False)

        gamemode.onlineSubsystemReference = request.onlineSubsystemReference
        gamemode.playersPerTeam = request.playersPerTeam
        gamemode.teams = request.teams
        gamemode.admissionFeePerPlayer = request.admissionFeePerPlayer
        gamemode.winRewardPerPlayer = request.winRewardPerPlayer
        gamemode.matchmakerAlgorithm = request.matchmakerAlgorithm
        gamemode.matchmakerDisparityMax = request.matchmakerDisparityMax

        gamemode.ads_allowed = request.ads_allowed
        gamemode.ads_require_approval = request.ads_require_approval
        gamemode.ads_required = request.ads_required
        gamemode.ads_default_textures = request.ads_default_textures
        gamemode.ads_per_match_maximum = request.ads_per_match_maximum
        gamemode.ads_minimum_bid_per_impression = request.ads_minimum_bid_per_impression
        gamemode.ads_description = request.ads_description

        gamemode.teamSizeMin = request.teamSizeMin
        gamemode.teamSizeMax = request.teamSizeMax

        gamemode.requireBadgeTags = request.requireBadgeTags

        gameModesController.update(gamemode)

        return GameModeResponse(
                key_id = gamemode.key.id(),

                gameKeyId = gamemode.gameKeyId,
                gameTitle = gamemode.gameTitle,
                onlineSubsystemReference = gamemode.onlineSubsystemReference,
                playersPerTeam = gamemode.playersPerTeam,
                teams = gamemode.teams,
                admissionFeePerPlayer = gamemode.admissionFeePerPlayer,
                winRewardPerPlayer = gamemode.winRewardPerPlayer,

                response_message='Success.',
                response_successful=True)


    @endpoints.method(GAME_MODE_RESOURCE, GameModeResponse, path='gameModeDelete', http_method='POST', name='mode.delete')
    def gameModeDelete(self, request):
        """ Delete a game mode - PROTECTED """
        logging.info("gameModeDelete")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameModescontroller = GameModesController()

        userController = UsersController()
        gameController = GamesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameModeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameModeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameModeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameModeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## TODO any more checks?

        ## delete the game mode
        entity = gameModescontroller.get_by_key_id(int(request.key_id))

        ## grab the game
        game = gameController.get_by_key_id(entity.gameKeyId)
        if not game:
            return GameModeResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameModeResponse(response_message='Error: This is not your game.', response_successful=False)

        gameModescontroller.delete(entity)

        return GameModeResponse(response_message='Success.', response_successful=True)


    ##################### GAME LEVELS
    @endpoints.method(GAME_LEVEL_RESOURCE, GameLevelResponse, path='gameLevelCreate', http_method='POST', name='level.create')
    def gameLevelCreate(self, request):
        """ Create a game level - PROTECTED """
        logging.info("gameLevelCreate")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameLevelsController = GameLevelsController()

        userController = UsersController()
        gameController = GamesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameLevelResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            return GameLevelResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelResponse(response_message='Error: This is not your game.', response_successful=False)

        ## TODO any more checks?

        ## add the game level
        game_level = gameLevelsController.create(
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            title = request.title,
            engineTravelUrlString = request.engineTravelUrlString,
            selectionProbability = request.selectionProbability,
            outgoingLinkMin = request.outgoingLinkMin,
            outgoingLinkMax = request.outgoingLinkMax,
            chanceToCreateReturnLink = request.chanceToCreateReturnLink,
            chanceToCreateRandomLink = request.chanceToCreateRandomLink,
            randomLinkLevelTraverse = request.randomLinkLevelTraverse,
            minimumCurrencyHold = request.minimumCurrencyHold,
            shard_count_maximum = request.shard_count_maximum,
            sharded_server_template = request.sharded_server_template,
            sharded_player_capacity_threshold = request.sharded_player_capacity_threshold,
            sharded_player_capacity_maximum = request.sharded_player_capacity_maximum,
        )

        return GameLevelResponse(response_message='Success.', response_successful=True)


    @endpoints.method(GAME_LEVELS_COLLECTION_PAGE_RESOURCE, GameLevelsCollection, path='gameLevelsCollectionDeveloperGetPage', http_method='POST', name='levels.collection.developer.get.page')
    def gameLevelsCollectionDeveloperGetPage(self, request):
        """ Get a collection of game levels """
        logging.info("gameLevelsCollectionDeveloperGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelsCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelsCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelsCollection(response_message='Error: No User Record Found. ', response_successful=False)

        gameLevelsController = GameLevelsController()
        gameController = GamesController()

        ## grab the game
        game = gameController.get_by_key_id(int(request.gameKeyId))
        if not game:
            return GameLevelsCollection(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelsCollection(response_message='Error: This is not your game.', response_successful=False)

        entities = gameLevelsController.list_by_gameKeyId(request.gameKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(GameLevelResponse(
                key_id = entity.key.id(),
                gameKeyId = entity.gameKeyId,
                gameTitle = entity.gameTitle,
                title = entity.title,
                engineTravelUrlString = entity.engineTravelUrlString,
                selectionProbability = entity.selectionProbability,
                outgoingLinkMin = entity.outgoingLinkMin,
                outgoingLinkMax = entity.outgoingLinkMax,
            ))

        response = GameLevelsCollection(
            game_levels = entity_list
        )

        return response

    @endpoints.method(GAME_LEVEL_RESOURCE, GameLevelResponse, path='gameLevelGet', http_method='POST', name='level.get')
    def gameLevelGet(self, request):
        """ Get a game level """
        logging.info("gameLevelGet")

        userController = UsersController()
        gameController = GamesController()
        gameLevelsController = GameLevelsController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game level
        gamelevel = gameLevelsController.get_by_key_id(int(request.key_id))
        if not gamelevel:
            return GameLevelResponse(response_message='Error: Game Level not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(gamelevel.gameKeyId)
        if not game:
            return GameLevelResponse(response_message='Error: Game not found', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelResponse(response_message='Error: This is not your game.', response_successful=False)

        return GameLevelResponse(
                key_id = gamelevel.key.id(),

                gameKeyId = gamelevel.gameKeyId,
                gameTitle = gamelevel.gameTitle,
                title = gamelevel.title,
                engineTravelUrlString = gamelevel.engineTravelUrlString,
                selectionProbability = gamelevel.selectionProbability,
                outgoingLinkMin = gamelevel.outgoingLinkMin,
                outgoingLinkMax = gamelevel.outgoingLinkMax,

                chanceToCreateReturnLink = gamelevel.chanceToCreateReturnLink,
                chanceToCreateRandomLink = gamelevel.chanceToCreateRandomLink,
                randomLinkLevelTraverse = gamelevel.randomLinkLevelTraverse,

                minimumCurrencyHold = gamelevel.minimumCurrencyHold,
                shard_count_maximum = gamelevel.shard_count_maximum,
                sharded_server_template = gamelevel.sharded_server_template,
                sharded_player_capacity_threshold = gamelevel.sharded_player_capacity_threshold,
                sharded_player_capacity_maximum = gamelevel.sharded_player_capacity_maximum,

                response_message='Success.',
                response_successful=True)


    @endpoints.method(GAME_LEVEL_RESOURCE, GameLevelResponse, path='gameLevelUpdate', http_method='POST', name='level.update')
    def gameLevelUpdate(self, request):
        """ Update a game level - PROTECTED """
        logging.info("gameLevelUpdate")

        userController = UsersController()
        gameController = GamesController()
        gameLevelsController = GameLevelsController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameLevelResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game mode
        gamelevel = gameLevelsController.get_by_key_id(int(request.key_id))
        if not gamelevel:
            return GameLevelResponse(response_message='Error: Game level not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(gamelevel.gameKeyId)
        if not game:
            return GameLevelResponse(response_message='Error: Game not found', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelResponse(response_message='Error: This is not your game.', response_successful=False)

        gamelevel.title = request.title
        gamelevel.engineTravelUrlString = request.engineTravelUrlString
        gamelevel.selectionProbability = request.selectionProbability
        gamelevel.outgoingLinkMin = request.outgoingLinkMin
        gamelevel.outgoingLinkMax = request.outgoingLinkMax

        gamelevel.chanceToCreateReturnLink = request.chanceToCreateReturnLink
        gamelevel.chanceToCreateRandomLink = request.chanceToCreateRandomLink
        gamelevel.randomLinkLevelTraverse = request.randomLinkLevelTraverse

        gamelevel.minimumCurrencyHold = request.minimumCurrencyHold

        gamelevel.shard_count_maximum = request.shard_count_maximum
        gamelevel.sharded_server_template = request.sharded_server_template
        gamelevel.sharded_player_capacity_threshold = request.sharded_player_capacity_threshold
        gamelevel.sharded_player_capacity_maximum = request.sharded_player_capacity_maximum

        ## TODO - if these sharded settings have changed, we are going to need to go through and update the child servers.

        gameLevelsController.update(gamelevel)

        return GameLevelResponse(
                key_id = gamelevel.key.id(),

                gameKeyId = gamelevel.gameKeyId,
                gameTitle = gamelevel.gameTitle,
                title = gamelevel.title,
                engineTravelUrlString = gamelevel.engineTravelUrlString,
                selectionProbability = gamelevel.selectionProbability,
                outgoingLinkMin = gamelevel.outgoingLinkMin,
                outgoingLinkMax = gamelevel.outgoingLinkMax,

                response_message='Success.',
                response_successful=True)

    @endpoints.method(GAME_LEVEL_RESOURCE, GameLevelResponse, path='gameLevelDelete', http_method='POST', name='level.delete')
    def gameLevelDelete(self, request):
        """ Delete a game level - PROTECTED """
        logging.info("gameLevelDelete")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameLevelsController = GameLevelsController()

        userController = UsersController()
        gameController = GamesController()


        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameLevelResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)




        ## TODO any more checks?

        ## delete the game mode
        entity = gameLevelsController.get_by_key_id(int(request.key_id))

        ## grab the game
        game = gameController.get_by_key_id(entity.gameKeyId)
        if not game:
            return GameLevelResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelResponse(response_message='Error: This is not your game.', response_successful=False)

        gameLevelsController.delete(entity)

        return GameLevelResponse(response_message='Success.', response_successful=True)


    ##################### GAME LEVEL LINKS
    @endpoints.method(GAME_LEVEL_LINK_RESOURCE, GameLevelLinkResponse, path='gameLevelLinkCreate', http_method='POST', name='level.link.create')
    def gameLevelLinkCreate(self, request):
        """ Create a game level link - PROTECTED """
        logging.info("gameLevelLinkCreate")

        userController = UsersController()
        gameController = GamesController()
        gameLevelLinksController = GameLevelLinksController()
        gameLevelsController = GameLevelsController()

        userController = UsersController()
        gameController = GamesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameLevelLinkResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the gameLevel
        game_level = gameLevelsController.get_by_key_id(int(request.gameLevelKeyId))
        if not game_level:
            logging.info('game level not found')
            return GameLevelLinkResponse(response_message='Error: Game Level not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(game_level.gameKeyId)
        if not game:
            logging.info('game not found')
            return GameLevelLinkResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelLinkResponse(response_message='Error: This is not your game.', response_successful=False)

        ## TODO any more checks?

        # prevent null, we need to be able to look up by false
        if request.isReturnLink:
            isReturnLink = True
        else:
            isReturnLink = False

        ## add the game level link
        game_level_link = gameLevelLinksController.create(
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            gameLevelKeyId = game_level.key.id(),
            gameLevelTitle = game_level.title,

            locationX = request.locationX,
            locationY = request.locationY,
            locationZ = request.locationZ,
            selectionProbability = request.selectionProbability,

            resourcesUsedToTravel = request.resourcesUsedToTravel,
            resourceAmountsUsedToTravel = request.resourceAmountsUsedToTravel,
            currencyCostToTravel = request.currencyCostToTravel,

            isReturnLink = isReturnLink

        )

        return GameLevelLinkResponse(response_message='Success.', response_successful=True)


    @endpoints.method(GAME_LEVEL_LINKS_COLLECTION_PAGE_RESOURCE, GameLevelLinksCollection, path='gameLevelLinksCollectionDeveloperGetPage', http_method='POST', name='level.links.collection.developer.get.page')
    def gameLevelLinksCollectionDeveloperGetPage(self, request):
        """ Get a collection of game level links """
        logging.info("gameLevelLinksCollectionDeveloperGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelLinksCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelLinksCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelLinksCollection(response_message='Error: No User Record Found. ', response_successful=False)

        gameLevelsController = GameLevelsController()
        gameController = GamesController()
        gameLevelLinksController = GameLevelLinksController()

        ## grab the gameLevel
        game_level = gameLevelsController.get_by_key_id(int(request.gameLevelKeyId))
        if not game_level:
            return GameLevelLinksCollection(response_message='Error: Game Level not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(game_level.gameKeyId)
        if not game:
            return GameLevelLinksCollection(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelLinksCollection(response_message='Error: This is not your game.', response_successful=False)

        entities = gameLevelLinksController.list_by_gameLevelKeyId(request.gameLevelKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(GameLevelLinkResponse(
                key_id = entity.key.id(),
                gameKeyId = entity.gameKeyId,
                gameTitle = entity.gameTitle,
                gameLevelKeyId = entity.gameLevelKeyId,
                gameLevelTitle = entity.gameLevelTitle,
                locationX = entity.locationX,
                locationY = entity.locationY,
                locationZ = entity.locationZ,
                selectionProbability = entity.selectionProbability,
                resourcesUsedToTravel = entity.resourcesUsedToTravel,
                resourceAmountsUsedToTravel = entity.resourceAmountsUsedToTravel,
                currencyCostToTravel = entity.currencyCostToTravel,
                isReturnLink = entity.isReturnLink
            ))

        response = GameLevelLinksCollection(
            game_level_links = entity_list
        )

        return response

    @endpoints.method(GAME_LEVEL_LINK_RESOURCE, GameLevelLinkResponse, path='gameLevelLinkGet', http_method='POST', name='level.link.get')
    def gameLevelLinkGet(self, request):
        """ Get a game level link """
        logging.info("gameLevelLinkGet")

        userController = UsersController()
        gameController = GamesController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game level link
        gamelevellink = gameLevelLinksController.get_by_key_id(int(request.key_id))
        if not gamelevellink:
            return GameLevelLinkResponse(response_message='Error: Game Level Link not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(gamelevellink.gameKeyId)
        if not game:
            return GameLevelLinkResponse(response_message='Error: Game not found', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelLinkResponse(response_message='Error: This is not your game.', response_successful=False)

        return GameLevelLinkResponse(
                key_id = gamelevellink.key.id(),

                gameKeyId = gamelevellink.gameKeyId,
                gameTitle = gamelevellink.gameTitle,
                gameLevelKeyId = gamelevellink.gameLevelKeyId,
                gameLevelTitle = gamelevellink.gameLevelTitle,

                locationX = gamelevellink.locationX,
                locationY = gamelevellink.locationY,
                locationZ = gamelevellink.locationZ,
                selectionProbability = gamelevellink.selectionProbability,

                resourcesUsedToTravel = gamelevellink.resourcesUsedToTravel,
                resourceAmountsUsedToTravel = gamelevellink.resourceAmountsUsedToTravel,
                currencyCostToTravel = gamelevellink.currencyCostToTravel,
                isReturnLink = gamelevellink.isReturnLink,

                response_message='Success.',
                response_successful=True)


    @endpoints.method(GAME_LEVEL_LINK_RESOURCE, GameLevelLinkResponse, path='gameLevelLinkUpdate', http_method='POST', name='level.link.update')
    def gameLevelLinkUpdate(self, request):
        """ Update a game level link - PROTECTED """
        logging.info("gameLevelLinkUpdate")

        userController = UsersController()
        gameController = GamesController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameLevelLinkResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game level link
        gamelevellink = gameLevelLinksController.get_by_key_id(int(request.key_id))
        if not gamelevellink:
            return GameLevelLinkResponse(response_message='Error: Game level link not found with the supplied key', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(gamelevellink.gameKeyId)
        if not game:
            return GameLevelLinkResponse(response_message='Error: Game not found', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelLinkResponse(response_message='Error: This is not your game.', response_successful=False)

        gamelevellink.locationX = request.locationX
        gamelevellink.locationY = request.locationY
        gamelevellink.locationZ = request.locationZ
        gamelevellink.selectionProbability = request.selectionProbability
        gamelevellink.resourcesUsedToTravel = request.resourcesUsedToTravel
        gamelevellink.resourceAmountsUsedToTravel = request.resourceAmountsUsedToTravel
        gamelevellink.currencyCostToTravel = request.currencyCostToTravel

        gamelevellink.isReturnLink = request.isReturnLink

        gameLevelLinksController.update(gamelevellink)

        ## TODO check for changes that need to get propegated down to existing serverLinks

        return GameLevelLinkResponse(
                key_id = gamelevellink.key.id(),

                locationX = gamelevellink.locationX,
                locationY = gamelevellink.locationY,
                locationZ = gamelevellink.locationZ,
                selectionProbability = gamelevellink.selectionProbability,
                resourcesUsedToTravel = gamelevellink.resourcesUsedToTravel,
                resourceAmountsUsedToTravel = gamelevellink.resourceAmountsUsedToTravel,
                currencyCostToTravel = gamelevellink.currencyCostToTravel,

                response_message='Success.',
                response_successful=True)

    @endpoints.method(GAME_LEVEL_LINK_RESOURCE, GameLevelLinkResponse, path='gameLevelLinkDelete', http_method='POST', name='level.link.delete')
    def gameLevelLinkDelete(self, request):
        """ Delete a game level link - PROTECTED """
        logging.info("gameLevelLinkDelete")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()

        userController = UsersController()
        gameController = GamesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameLevelLinkResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameLevelLinkResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameLevelLinkResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameLevelLinkResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)




        ## TODO any more checks?

        ## delete the game level link
        entity = gameLevelLinksController.get_by_key_id(int(request.key_id))

        ## grab the game
        game = gameController.get_by_key_id(entity.gameKeyId)
        if not game:
            return GameLevelLinkResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameLevelLinkResponse(response_message='Error: This is not your game.', response_successful=False)

        gameLevelLinksController.delete(entity)

        return GameLevelLinkResponse(response_message='Success.', response_successful=True)


    ##################### GAME DATA
    @endpoints.method(GAME_DATA_RESOURCE, GameDataResponse, path='gameDataCreate', http_method='POST', name='data.create')
    def gameDataCreate(self, request):
        """ Create a game data record - PROTECTED """
        logging.info("gameDataCreate")

        userController = UsersController()
        gameController = GamesController()
        gameLevelLinksController = GameLevelLinksController()
        gameLevelsController = GameLevelsController()
        gameDataController = GameDataController()

        userController = UsersController()
        gameController = GamesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameDataResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameDataResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameDataResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameDataResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game
        game = gameController.get_by_key_id(request.gameKeyId)
        if not game:
            logging.info('game not found')
            return GameDataResponse(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameDataResponse(response_message='Error: This is not your game.', response_successful=False)

        ## TODO any more checks?


        ## add the game data
        game_data = gameDataController.create(
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            firebaseUser = authorized_user.firebaseUser,
            customKey = request.customKey,
            data = request.data

        )

        return GameDataResponse(response_message='Success.', response_successful=True)


    @endpoints.method(GAME_DATA_COLLECTION_PAGE_RESOURCE, GameDataCollection, path='gameDataCollectionDeveloperGetPage', http_method='POST', name='data.collection.developer.get.page')
    def gameDataCollectionDeveloperGetPage(self, request):
        """ Get a collection of game data records """
        logging.info("gameDataCollectionDeveloperGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameDataCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameDataCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameDataCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gameLevelsController = GameLevelsController()
        gameController = GamesController()
        gameLevelLinksController = GameLevelLinksController()
        gameDataController = GameDataController()

        ## grab the game
        game = gameController.get_by_key_id(request.gameKeyId)
        if not game:
            return GameDataCollection(response_message='Error: Game not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game.userKeyId:
            return GameDataCollection(response_message='Error: This is not your game.', response_successful=False)

        entities = gameDataController.list_by_gameKeyId(request.gameKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(GameDataResponse(
                key_id = entity.key.id(),
                customKey = entity.customKey,
                #data = request.data
            ))

        response = GameDataCollection(
            game_data = entity_list
        )

        return response

    @endpoints.method(GAME_DATA_RESOURCE, GameDataResponse, path='gameDataGet', http_method='POST', name='data.get')
    def gameDataGet(self, request):
        """ Get a game data record """
        logging.info("gameDataGet")

        userController = UsersController()
        gameController = GamesController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()
        gameDataController = GameDataController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameDataResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameDataResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameDataResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game level link
        game_data = gameDataController.get_by_key_id(int(request.key_id))
        if not game_data:
            logging.info('game data not found')
            return GameDataResponse(response_message='Error: Game data not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game_data.userKeyId:
            logging.info("not the users game")
            return GameDataResponse(response_message='Error: This is not your game.', response_successful=False)

        return GameDataResponse(
                key_id = game_data.key.id(),
                customKey = game_data.customKey,
                data = game_data.data,
                response_message='Success.',
                response_successful=True)


    @endpoints.method(GAME_DATA_RESOURCE, GameDataResponse, path='gameDataUpdate', http_method='POST', name='data.update')
    def gameDataUpdate(self, request):
        """ Update a game data record - PROTECTED """
        logging.info("gameDataUpdate")

        userController = UsersController()
        gameController = GamesController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()
        gameDataController = GameDataController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameDataResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameDataResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameDataResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameDataResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game data
        game_data = gameDataController.get_by_key_id(int(request.key_id))
        if not game_data:
            return GameDataResponse(response_message='Error: Game data not found with the supplied key', response_successful=False)

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == game_data.userKeyId:
            return GameDataResponse(response_message='Error: This is not your game.', response_successful=False)

        game_data.customKey = request.customKey
        game_data.data = request.data

        gameDataController.update(game_data)

        return GameDataResponse(
                key_id = game_data.key.id(),
                response_message='Success.',
                response_successful=True)

    @endpoints.method(GAME_DATA_RESOURCE, GameDataResponse, path='gameDataDelete', http_method='POST', name='data.delete')
    def gameDataDelete(self, request):
        """ Delete a game data record - PROTECTED """
        logging.info("gameDataDelete")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameLevelsController = GameLevelsController()
        gameLevelLinksController = GameLevelLinksController()
        gameDataController = GameDataController()

        userController = UsersController()
        gameController = GamesController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameDataResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameDataResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameDataResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GameDataResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## TODO any more checks?

        ## delete the game level link
        entity = gameDataController.get_by_key_id(int(request.key_id))

        ## make sure this user is the owner of the game
        if not authorized_user.key.id() == entity.userKeyId:
            return GameDataResponse(response_message='Error: This is not your game.', response_successful=False)

        gameDataController.delete(entity)

        return GameDataResponse(response_message='Success.', response_successful=True)


    @endpoints.method(GAME_PLAYER_RESOURCE, GamePlayerResponse, path='metaGamePlayerConnect', http_method='POST', name='metagame.player.connect')
    def metaGamePlayerConnect(self, request):
        """ Connect a game player """
        logging.info("metaGamePlayerConnect")

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamePlayerResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if not game:
            logging.error('game not found')
            return GamePlayerResponse(response_message='Error: Game not found with the supplied key', response_successful=False)


        logging.info('not developer request')

        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())
        if not game_player:
            logging.warning('game player not found')
            return GamePlayerResponse(response_message='Error:  Game Player Not Found.', response_successful=False, gameTrustable = game.trustable,)
        else:
            ## only allow connecting successfully one time.
            if not game_player.metagame_connected:
                ## generate a new api key to use as a security code for this game player
                apiKey = gamePlayerController.create_unique_api_key()
                game_player.apiKey = apiKey;
                gamePlayerController.update(game_player)

                return GamePlayerResponse(
                        key_id = game_player.key.id(),
                        apiKey = game_player.apiKey,
                        response_message='Success.',
                        response_successful=True)
            else:
                logging.info("metagame already connected - rejecting")
                return GamePlayerResponse(
                        response_message='Metagame already connected for this player.',
                        response_successful=False)

    @endpoints.method(GAMES_RESOURCE, GamesResponse, path='gamePatchDeploy', http_method='POST', name='patch.deploy')
    def gamePatchDeploy(self, request):
        """ Deploy a new patch - PROTECTED """
        logging.info("gamePatchDeploy")

        userController = UsersController()
        gameController = GamesController()
        serverController = ServersController()
        chatChannelController = ChatChannelsController()

        ## This endpoint will be called by a developer using the dev backend.
        ## They will be submitting a new XML patch manifest, a new disk image name, the server shutdown message, and a time to wait
        ## we'll save these values, and send out the server shutdown message
        ## Then queue up the tak to run after the designated number of seconds.
        ## The task does all the work of checking servers, shutting them down, and doing any cleanup.



        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GamesResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        ## grab the game
        game = gameController.get_by_key_id(int(request.key_id))
        if game.patcher_patching:
            logging.info('Error: Patcher already patching!  Aborting.')
            return GamesResponse(response_message='Error: Patcher already patching!  Aborting.', response_successful=False)

        ## make sure this user owns this game!!!
        if game.userKeyId != authorized_user.key.id():
            logging.info('only the owner can do this')
            return GamesResponse(response_message='Error: Only the game owner can do this!  Aborting.', response_successful=False)



        game.patcher_patching = True;

        game.patcher_prepatch_xml = request.patcher_prepatch_xml
        game.patcher_server_shutdown_seconds = request.patcher_server_shutdown_seconds
        game.patcher_server_shutdown_warning_chat = request.patcher_server_shutdown_warning_chat
        game.patcher_server_disk_image = request.patcher_server_disk_image

        gameController.update(game)

        ## Get all of the active servers for the game
        ## Send a message to the channel for this server
        servers = serverController.get_provisioned_by_game_key_id(game.key.id())
        for server in servers:
            logging.info('found active server')

            server_chat_channel = chatChannelController.get_by_channel_type_refKeyId('server', server.key.id())
            if server_chat_channel:
                logging.info('found server chat channel')

                taskUrl='/task/chat/channel/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': server_chat_channel.key.id(),
                                                                                    "message": request.patcher_server_shutdown_warning_chat,
                                                                                    #"userKeyId": authorized_user.key.id(),
                                                                                    #"userTitle": authorized_user.title,
                                                                                    "chatMessageKeyId": uuid.uuid4(),
                                                                                    "chatChannelTitle": server_chat_channel.title,
                                                                                    "chatChannelRefType":server_chat_channel.channel_type,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })



        ## Send a message to the game admin discord channel
        if game.discord_subscribe_config_changes and game.discord_webhook_admin:

            try:
                name = claims['name']
            except:
                name = claims['email']

            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Deploying new patch in %s by: %s | %s" % (request.patcher_server_shutdown_seconds, name, claims['email'])
            discord_data = { "embeds": [{"title": "Patch Deploying", "url": "https://example.com", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)


        ## Send a message to the game public channel - this should be customizable!
        if game.discord_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = request.patcher_discord_message
            url = "https://uetopia.com/game/%s" % str(game.key.id())
            discord_data = { "embeds": [{"title": "Patch Deploying", "url": url, "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook,
                              "POST",
                              data,
                              headers=headers)


        ## set up the task that will do all of the server management work
        taskUrl='/task/game/patch/apply'
        taskqueue.add(url=taskUrl, queue_name='taskGamePatcher', params={'key_id': game.key.id()
                                                                        }, countdown=request.patcher_server_shutdown_seconds)


        return GamesResponse(
                key_id = game.key.id(),
                response_message='Success.  Patch Queued.',
                response_successful=True)
