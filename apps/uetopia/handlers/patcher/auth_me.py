import logging
import json
from apps.handlers import BaseHandler
#from google.appengine.api import users
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from google.appengine.api import urlfetch
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.user_login_tokens import UserLoginTokensController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class IndexHandler(BaseHandler):
    """
    THis handler provides authentication for the ZLauncher based patcher.
    After authentication completes, it will request this page.
    We return auth details and the list of all of the patchable games that this user has access to

    """
    def get(self):
        """ Static Index

        """
        #user = users.get_current_user()
        usersController = UsersController()
        ultController = UserLoginTokensController()
        gamePlayerController = GamePlayersController()
        gameController = GamesController()

        ## check access token - get user by token
        claims = google.oauth2.id_token.verify_firebase_token(self.request.get('access_token'), HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return self.render_json_response(
                auth=True,
                id=None,
                AuthTicket = None
                )
        else:
            logging.info('firebase auth')
            authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('user not found')
                return self.render_json_response(
                    auth=True,
                    id=None,
                    AuthTicket = None
                    )

        #user_token = ultController.get_by_access_token(self.request.get('access_token'))

        #if not user_token:

        patchable_game_list = []

        # get the game players for this user
        game_players = gamePlayerController.get_list_by_userKeyId(authorized_user.key.id())
        for game_player in game_players:
            logging.info('found game player')

            ## get the game
            this_gp_game = gameController.get_by_key_id(game_player.gameKeyId)
            if this_gp_game:
                logging.info('found game')
                if this_gp_game.patcher_enabled:
                    logging.info('patcher enabled')
                    patchable_game_list.append(this_gp_game.to_json_for_patcher())


        ## get the IP address to use from our socket.io server:
        #SocketIpAddress = "http://uetopia.herokuapp.com"

        return self.render_json_response(
            auth=True,
            id=str(authorized_user.key.id()),
            ##userId=user_token.userKeyId,
            AuthTicket = "testTicket",
            SocketIpAddress = HEROKU_SOCKETIO_SERVER,
            firebaseUser = authorized_user.firebaseUser,
            patchable_game_list = patchable_game_list
            )
