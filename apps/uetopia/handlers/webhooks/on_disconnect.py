import logging
import json
import time
import hashlib
import hmac
import urllib
import httplib
import base64
import uuid
from collections import OrderedDict
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
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.games import GamesController

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class OnDisconnectHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def post(self):
        """ Static Index

        """
        logging.info(self.request.body)

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        if jsonobject:

            usersController = UsersController()
            gamePlayersController = GamePlayersController()
            matchController = MatchController()
            mpController = MatchPlayersController()
            gameController = GamesController()

            user = usersController.get_by_firebaseUser(jsonobject['user_id'])
            if not user:
                logging.info('user not found')
                return self.render_json_response(
                    response_successful = False,
                    response_message = "User not found"
                    )


            ## update firebase
            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(), 'online': False, 'skip_presence': True }, countdown = 2,)

            ## update friends
            taskUrl='/task/user/friends/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                            'online': False,
                                                                            #'playingGame': game.title,
                                                                            #'playingGameKeyId': game.key.id(),
                                                                            #'playingOnServer': playingOnServer,
                                                                            #'playingOnServerKeyId': playingOnServerKeyId,
                                                                            #'playingLink': playingLink
                                                                            }, countdown = 2,)


            ## also check to see if matchmaker is running - a player could have started matchmaker and quit or crashed.
            match_players = mpController.list_pending_by_userKeyId(user.key.id())

            for match_player in match_players:
                logging.info('found a pending match player')
                match_player.matchmakerStarted = False
                match_player.matchmakerPending = False
                match_player.matchmakerJoinPending = False
                match_player.matchTaskStatusKeyId = None
                mpController.update(match_player)

                ## check to see if this wasa metagame matchmaker so we can send an API request out to the metagame server

                if match_player.matchmakerMode == "metagame":
                    logging.info('this was a metagame matchmaker')

                    game = gameController.get_by_key_id(match_player.gameKeyId)
                    if game:
                        logging.info('found game')


                        if game.match_allow_metagame and game.match_metagame_api_url:
                            logging.info('metagame enabled and API endpoint found.')

                            uri = "/api/v1/metagame/player_end"

                            ## send params as json.
                            json_params = OrderedDict([
                                ("nonce", time.time()),
                                ("player_key_id", match_player.gamePlayerKeyId)
                            ])

                            json_encoded = json.dumps(json_params)

                            # Hash the params string to produce the Sign header value
                            H = hmac.new(str(game.apiSecret), digestmod=hashlib.sha512)
                            H.update(json_encoded)
                            sign = H.hexdigest()

                            headers = {"Content-type": "application/x-www-form-urlencoded",
                                               "Key":game.apiKey,
                                               "Sign":sign}

                            conn = httplib.HTTPSConnection(game.match_metagame_api_url)

                            conn.request("POST", uri, json_encoded, headers)
                            response = conn.getresponse()

                            #logging.info(response.read())

                            ## parse the response
                            jsonstring = str(response.read())
                            logging.info(jsonstring)
                            jsonobject = json.loads(jsonstring)

                            # do something with the response
                            if not jsonobject['request_successful']:
                                logging.info('the metagame API request was unsuccessful')

                                return self.render_json_response(
                                    response_message='MetaGame API request failed.',
                                    response_successful=False
                                )

                            #logging.info('validation was successful')



            ## set this specific game player
            #game_players = gamePlayersController.get_by_gameKeyId_userKeyId(game.key.id(), user.key.id())
            #if game_player:
            #    if game_player.online:
            #        game_player.online = False
            #        gamePlayersController.update(game_player)


            ## set all of the server players?

            ## set group members?


        return self.render_json_response(
            response_successful = True,
            response_message = "Processed Request"
            )
