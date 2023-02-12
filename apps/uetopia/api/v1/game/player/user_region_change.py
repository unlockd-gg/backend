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

class UserRegionChangeHandler(BaseHandler):
    def post(self):
        """
        Get Servers for a game/user
        Requires http headers:  -
        Requires POST parameters:  - regionIn
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

        ## parse the incoming json
        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)
        ## encryption = jsonobject["encryption"]

        game = gameController.get_by_key_id(int(jsonobject['gameKeyIdStr']))
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
            return self.render_json_response(
                authorization = False,
                message='game player not found',
                success = False,
                servers = []
            )


        if jsonobject['region']:
            user.region = jsonobject['region']


            #######################
            ## Check the game player for region match.
            ## Inside of gamePlayer is a reference to lastServerClusterKeyId
            ## This is mapped to a region, indexed.

            ## look up the server cluster for this game region
            ## if not, send a chat to the user informing thhem that the matchmaker region was changed, but they need to visit the game page to update social region.
            ## if it exists, set this cluster in the game player

            region_server_cluster = serverClusterController.get_by_gameKeyId_vm_region(game.key.id(), jsonobject['region'] )
            if not region_server_cluster:
                logging.info('did not find matching server cluster')
                chat_message = "Matchmaker region changed.  Server cluster not changed. "
            else:
                logging.info('found matching server cluster')
                chat_message = "Matchmaker and server cluster region changed. "
                game_player.lastServerClusterKeyId = region_server_cluster.key.id()

                gamePlayerController.update(game_player)


            userController.update(user)


            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                "message": chat_message,
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })


        return self.render_json_response(
            authorization = True,
            success = True
        )
