import logging
import json
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
from apps.uetopia.controllers.user_login_tokens import UserLoginTokensController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class OnConnectHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def post(self):
        """ Static Index

        """
        logging.info('OnConnect')
        logging.info(self.request.body)

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        if jsonobject:

            usersController = UsersController()
            gameController = GamesController()
            gamePlayersController = GamePlayersController()

            ## set the user to online
            ## using firebaseUserId for now
            ## TODO use the auth token instead.

            user = usersController.get_by_firebaseUser(jsonobject['user_id'])
            if not user:
                logging.info('user not found')
                return self.render_json_response(
                    response_successful = False,
                    response_message = "User not found"
                    )

            game = gameController.get_by_key_id(int(jsonobject['gameKeyId']))
            if not game:
                logging.info('game not found')
                return self.render_json_response(
                    response_successful = False,
                    response_message = "Game not found"
                    )


            #user.online = False
            #usersController.update(user)

            playingLink = '/#/game/%s'%game.key.id()

            ## set all of the user relationships
            taskUrl='/task/user/friends/firebase/update'
            if user.twitch_streamer:

                logging.info('twitch streamer found - checking stream status')
                headers = {"Content-Type": "application/json", "Client-ID": TWITCH_CLIENT_ID}
                URL = "https://api.twitch.tv/helix/streams?user_id=%s" % user.twitch_channel_id

                try:
                    resp, content = http_auth.request(URL,
                                        "GET",
                                      ##"PUT", ## Write or replace data to a defined path,
                                      #user_json,
                                      headers=headers)

                    #logging.info(resp)
                    logging.info(content)
                    stream_info_json = json.loads(content)
                    if stream_info_json['stream']:
                        logging.info('stream info found')
                        user.twitch_currently_streaming = True
                        user.twitch_stream_game = stream_info_json['stream']['game']
                        user.twitch_stream_viewers = stream_info_json['stream']['viewers']
                    else:
                        user.twitch_currently_streaming = False
                except:
                    user.twitch_currently_streaming = False
                    user.twitch_stream_game = ""
                    user.twitch_stream_viewers = 0

                streamLink='https://www.twitch.tv/%s'%user.twitch_channel_id
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                                    'online': True,
                                                                                    'streaming': user.twitch_currently_streaming,
                                                                                    'streamLink':streamLink,
                                                                                    'playingGame': game.title,
                                                                                    'playingGameKeyId': game.key.id(),
                                                                                    #'playingOnServer': playingOnServer,
                                                                                    #'playingOnServerKeyId': playingOnServerKeyId,
                                                                                    'playingLink': playingLink}, countdown = 2,)

            else:
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                                'online': True,
                                                                                'playingGame': game.title,
                                                                                'playingGameKeyId': game.key.id(),
                                                                                #'playingOnServer': playingOnServer,
                                                                                #'playingOnServerKeyId': playingOnServerKeyId,
                                                                                'playingLink': playingLink}, countdown = 2,)


            ## set this specific game player
            game_player = gamePlayersController.get_by_gameKeyId_userKeyId(game.key.id(), user.key.id())
            if game_player:
                if not game_player.online:
                    game_player.online = True
                    gamePlayersController.update(game_player)


            ## set all of the server players?

            ## set group members?


        return self.render_json_response(
            response_successful = True,
            response_message = "Processed Request"
            )
