import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from httplib2 import Http
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.utilities.server_shard_detect_init import detect_init_shard_server

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class UserServersHandler(BaseHandler):
    def get(self, gameKeyId, userKeyId):
        """
        Get Servers for a game/user
        Requires http headers:  -
        Requires POST parameters:  -
        """
        serverController = ServersController()
        usersController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()
        gameCharacterController = GameCharactersController()
        serverClusterController = ServerClustersController()
        teamController = TeamsController()
        teamMemberController = TeamMembersController()
        serverShardController = ServerShardsController()
        serverShardPlaceholderController = ServerShardPlaceholderController()

        ## Run auth.  we have our JWT
        userController = usersController

        try:
            id_token = self.request.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')

        if id_token:
            logging.info("id_token: %s" %id_token)

            # Verify Firebase auth.
            #logging.info(self.request_state)

            claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
            if not claims:
                logging.error('Firebase Unauth')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                )

            user = userController.get_by_firebaseUser(claims['user_id'])

            if not user:
                logging.info('no user record found')
                return self.render_json_response(
                    authorization = False,
                    message='user not found',
                    success = False,
                    servers = []
                )
        else:
            return self.render_json_response(
                authorization = False,
                message='user not found',
                success = False,
                servers = []
            )

        game = gameController.get_by_key_id(int(gameKeyId))
        if not game:
            logging.info('game not found')
            return self.render_json_response(
                authorization = False,
                message='game not found',
                success = False,
                servers = []
            )




        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(game.key.id(), user.key.id())
        if not game_player:
            logging.info('game player not found')

            ## this can happen if a user is using two differnt accounts
            ## create the game player
            ## it's safe to just create it.  IS IT THOUGH?
            ## maybe duplicates?
            ## TODO CHECK THE FEED

            ## just assign a server cluster at random
            selected_server_cluster = serverClusterController.get_by_gameKeyId(game.key.id())
            lastServerClusterKeyId = selected_server_cluster.key.id()

            game_player = gamePlayerController.create(
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                userKeyId = user.key.id(),
                userTitle = user.title,
                locked = False,
                online = True,
                rank = 1600,
                score = 0,
                #autoAuth = True,
                #autoAuthThreshold = 10000,
                autoTransfer = True,
                firebaseUser = user.firebaseUser,
                picture = user.picture,
                lastServerClusterKeyId = lastServerClusterKeyId,
                groupKeyId = user.groupTagKeyId,
                groupTag = user.groupTag,
                showGameOnProfile = True
            )

            if game.discord_subscribe_new_players and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "New Player: %s | %s" % (user.key.id(), user.title)
                url = "http://ue4topia.appspot.com/#/user/%s" % user.key.id()
                discord_data = { "embeds": [{"title": "New Player", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)



        #if not game_player.lastServerClusterKeyId:
        #    logging.info('game player lastServerClusterKeyId not found')
        #    return self.render_json_response(
        #        authorization = False,
        #        message='game player lastServerClusterKeyId not found',
        #        success = False,
        #        servers = []
        #    )

        ## before doing anything else, check for an existing placeholder.
        ## If there is a placeholder, we are only interested in this server.
        existing_placeholder = serverShardPlaceholderController.get_by_userKeyId_gameKeyId(game_player.userKeyId, game.key.id())

        if existing_placeholder:
            logging.info('found an existing placeholder')

            ## 8.7.2021
            ## Sometimes, there can be an existing placeholder, but the ShardKeyId is missing.
            ## check for it first
            if existing_placeholder.serverShardKeyId:

                server_shard = serverShardController.get_by_key_id(existing_placeholder.serverShardKeyId)

                if server_shard:
                    logging.info('found server shard record')

                    if server_shard.online:
                        logging.info('server shard is online')

                        server = serverController.get_by_key_id(server_shard.serverShardKeyId)

                        if server:
                            logging.info('found server')

                            servers_response = []
                            servers_response.append(server.to_json_for_session())

                            return self.render_json_response(
                                authorization = True,
                                success = True,
                                servers = servers_response
                            )

            logging.info('there was a placeholder, but something was wrong.  Aborting')

            return self.render_json_response(
                authorization = True,
                success = False,
                servers = []
            )


        ## if the game uses characters, we need the active character
        if game.characters_enabled:
            logging.info('characters enabled')
            if game_player.characterCurrentKeyId:
                logging.info('found a characterCurrentKeyId')
                game_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
            else:
                logging.info('but there was no characterCurrentKeyId')
                game_character = None

        ## if a player is created before the server cluster is created, in DEV, this could potentially be null
        ## make sure it exists first, otherwise, assign one at random
        if game_player.lastServerClusterKeyId:
            server_cluster = serverClusterController.get_by_key_id(game_player.lastServerClusterKeyId)
            if not server_cluster:
                logging.info('server_cluster not found')
                return self.render_json_response(
                    authorization = False,
                    message='server_cluster not found',
                    success = False,
                    servers = []
                )
        else:
            ## last server cluster was not set - rare edge case...  Assign one.

            ## pick one that matches the player's selected region if available
            server_cluster = serverClusterController.get_by_gameKeyId_vm_region(game.key.id(), user.region)

            if server_cluster:
                logging.info('found a server cluster that matches the users region.')

            else:
                logging.info('did not find a server cluster for the user region - assigning a random one')
                server_cluster = serverClusterController.get_by_gameKeyId(game.key.id())

            game_player.lastServerClusterKeyId = server_cluster.key.id()

            gamePlayerController.update(game_player)

        ## can we show all of the servers?
        if server_cluster.travelMode == "free":
            logging.info('server cluster travel mode is set to free.')

            servers = serverController.get_provisioned_by_gameKeyId_serverClusterKeyId(game.key.id(), server_cluster.key.id() )

            servers_response = []

            for server in servers:
                ## don't show full shards
                if server.sharded_from_template:
                    logging.info('found a shard - looking up current state')

                    ## 3/18/20 - Shard Manager should be invoked here instead so we can get the user on the correct shard

                    ## leaving it alone for now since this is FREE travel mode.

                    ## Are there any shards online with room?
                    s_shard = serverShardController.get_by_serverShardKeyId(server.key.id())
                    if s_shard:
                        logging.info('got shard data')
                        if s_shard.online and s_shard.playerCount < s_shard.playerCapacityThreshold:
                            logging.info('this shard is online and still has space below the threshold')

                            ## Are there placeholders already claiming these slots?


                            servers_response.append(server.to_json_for_session())



                    ## If so, just send it back and add a placeholder record so we can keep track of it.


                else:
                    logging.info('not a sharded server - adding')
                    servers_response.append(server.to_json_for_session())

            return self.render_json_response(
                authorization = True,
                success = True,
                servers = servers_response
            )

        else:
            logging.info('server cluster travel mode is restricted')

            find_welcome_server = False

            if game.characters_enabled:
                ## Do character
                if game_character:
                    if not game_character.lastServerKeyId:
                        logging.info('game character lastServerKeyId not found')
                        find_welcome_server = True

            else:
                if not game_player.lastServerKeyId:
                    logging.info('game player lastServerKeyId not found')
                    find_welcome_server = True

            ## also send to welcome if server lcuster is set to always do it
            if server_cluster.rejoiningPlayerStartMode == "random entry":
                logging.info('this cluster is set to random entry')
                find_welcome_server = True


            if find_welcome_server:
                ## send to entry
                server = serverController.get_random_entry_by_gameKeyId_serverClusterKeyId(game.key.id(), server_cluster.key.id() )

                if server:
                    logging.info('found a random entry server')
                    ## check for sharded server
                    if server.sharded_server_template:
                        logging.info('found sharded entry server')

                        ## we need to get all of the player / team information at this point

                        ## get the user's team/party (if any)
                        team = None
                        team_member = teamMemberController.get_by_gameKeyId_userKeyId(game.key.id(), user.key.id())
                        if team_member:
                            team = teamController.get_by_key_id(team_member.teamKeyId)

                        server_to_use = detect_init_shard_server(server, user, team, team_member)

                    else:
                        logging.info('not a sharded server')
                        server_to_use = server

                    ## only send it if the server is ready.
                    if server_to_use:
                        logging.info('found server_to_use')
                        if server_to_use.continuous_server_provisioned:
                            logging.info('it is provisioned')

                            servers_response = []
                            servers_response.append(server_to_use.to_json_for_session())

                            return self.render_json_response(
                                authorization = True,
                                success = True,
                                servers = servers_response
                            )
                        else:
                            return self.render_json_response(
                                authorization = True,
                                success = True,
                                servers = []
                            )

                    else:
                        return self.render_json_response(
                            authorization = True,
                            success = True,
                            servers = []
                        )
                else:
                    logging.error('could not find a server.  Make sure you have an entry server set to random chance 1.0')

            ## if we are here, we have a server id that we can use
            logging.info('found a lastServerKeyId')
            ## in the case of a sharded server, this points to the shard itself,
            ## so we don't need to do anything special here.
            if game.characters_enabled and game_character:
                logging.info('getting last server from character')
                server = serverController.get_by_key_id(game_character.lastServerKeyId)
            else:
                logging.info('getting last server from player')
                server = serverController.get_by_key_id(game_player.lastServerKeyId)

            ## check if it is a shard
            if server.sharded_from_template:
                logging.info('sharded_from_template')


                ## get the server_shard record so we can check the player count
                server_shard = serverShardController.get_by_serverShardKeyId(server.key.id())
                if not server_shard:
                    logging.error('server shard record was not found')
                if server_shard.online:
                    logging.info('shard is online')
                    if server_shard.playerCount < server_shard.playerCapacityMaximum:
                        logging.info('shard has room')

                        ## only send it if the server is ready.
                        if server.continuous_server_provisioned:
                            logging.info('server is provisioned')

                            servers_response = []
                            servers_response.append(server.to_json_for_session())

                            return self.render_json_response(
                                authorization = True,
                                success = True,
                                servers = servers_response
                            )
                        else:
                            logging.info('server not actually provisioned')

                    else:
                        logging.info('shard does not have room')

                else:
                    logging.info('shard not online')



                ## find another shard if there are any online
                ## we don't want to use the server_shard_detect_init utility here, because this is going to be called frequesntly, and overlaps with AttemptserverAllocate

                ## we need to look at the server shards records to find one that is online and has room
                ## if we find one, look up the server, make sure it is provisioned, and return it
                all_shards = serverShardController.get_list_by_serverShardTemplateKeyId(server.sharded_from_template_serverKeyId)
                for possible_shard in all_shards:
                    logging.info('checking shard')

                    if possible_shard.online:
                        logging.info('shard is online')

                        if possible_shard.playerCount < possible_shard.playerCapacityMaximum:
                            logging.info('shard has room')

                            ## get the server and make sure it is provisioned
                            server = serverController.get_by_key_id(possible_shard.serverShardKeyId)
                            if not server:
                                logging.error('server not found by key')

                            ## only send it if the server is ready.
                            if server.continuous_server_provisioned:
                                logging.info('server is provisioned')

                                servers_response = []
                                servers_response.append(server.to_json_for_session())

                                return self.render_json_response(
                                    authorization = True,
                                    success = True,
                                    servers = servers_response
                                )


            ## it's not a shard treat it like normal
            ## only send it if the server is ready.
            if server.continuous_server_provisioned:
                logging.info('server is provisioned')

                servers_response = []
                servers_response.append(server.to_json_for_session())

                return self.render_json_response(
                    authorization = True,
                    success = True,
                    servers = servers_response
                )

            else:
                return self.render_json_response(
                    authorization = True,
                    success = True,
                    servers = []
                )
