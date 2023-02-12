import logging
import datetime
import string
import json
import time
import hashlib
import hmac
import urllib
import httplib
from collections import OrderedDict
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from httplib2 import Http
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.match_task_status import MatchTaskStatusController
from apps.uetopia.controllers.team_members import TeamMembersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class MatchmakerCancelHandler(BaseHandler):
    def post(self, gameKeyId):
        """
        Cancel Matchmaking for a game
        Requires http headers:  -
        Requires POST parameters:  - userid, matchtype
        """

        ## Run auth.  we have our JWT
        userController = UsersController()

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
                    authorization = True,
                    success = False,
                )

        ## check this userid
        ## get the game player
        ## are there any existing matches

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        gpController = GamePlayersController()
        mtsController = MatchTaskStatusController()
        mpController = MatchPlayersController()
        gmController = GameModesController()
        gameController = GamesController()
        teamMembersController = TeamMembersController()

        userid = user.key.id()

        ## update the match player to be disabled for matchmaker
        ## prevent them from showing up in the task
        match_player = mpController.get_pending_by_gameKeyId_userKeyId(int(gameKeyId), userid)

        if not match_player:
            logging.error('no match player found, this can happen if a player starts matchmaking, quits the game, a match is found, starts matchmaking, but the server is not online yet.')

            ## send out a chat message
            ## Setup for pushes out to heroku
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            textMessage = "> Matchmaker could not be cancelled.  You have an active match, but the server has not come online yet.  "

            chat_msg = json.dumps({"type":"chat",
                                    "textMessage":textMessage,
                                    "userKeyId": "SYSTEM",
                                    "userTitle": "SYSTEM",
                                    #"chatMessageKeyId": chatMessageKeyId,
                                    #"chatChannelTitle": channel.title,
                                    #"chatChannelKeyId": channel.key.id(),
                                    "created":datetime.datetime.now().isoformat()
            })
            return self.render_json_response(
                authorization = True,
                success = True,
                #servers = servers_response
            )

        ## team?
        current_user_team_member = teamMembersController.get_by_gameKeyId_userKeyId(int(gameKeyId), userid)
        if current_user_team_member:
            logging.info('found a team meber record')
            if not current_user_team_member.captain:
                logging.info('User is not captain - aborting')

                if game.discord_subscribe_errors and game.discord_webhook_admin:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Error: %s attempted to cancel matchmaking, but is not the team captain" % (user.title)
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "you are not the captain of your team."
                )

            ## We have the captain.

            ## Any other checks?
            ## get all of the team members
            all_team_members = teamMembersController.get_by_teamKeyId(current_user_team_member.teamKeyId)

            for team_member in all_team_members:
                team_match_player = mpController.get_pending_by_gameKeyId_userKeyId(int(gameKeyId), team_member.userKeyId)

                team_match_player.matchmakerStarted = False
                team_match_player.matchmakerPending = False
                team_match_player.matchmakerJoinPending = False
                team_match_player.matchTaskStatusKeyId = None
                mpController.update(team_match_player)

                ## send out a chat message
                ## Setup for pushes out to heroku
                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                headers = {"Content-Type": "application/json"}

                textMessage = "> Matchmaker Cancelled"

                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
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
                    URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, team_match_player.firebaseUser)
                    resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      chat_msg,
                                      headers=headers)

                    logging.info(resp)
                    logging.info(content)
                except:
                    logging.error('heroku error')


        ## check to see if this was a metagame matchmaker so we can send an API request out to the metagame server

        if match_player:
            if match_player.matchmakerMode:
                if match_player.matchmakerMode == "metagame":
                    logging.info('this was a metagame matchmaker')

                    game = gameController.get_by_key_id(int(gameKeyId))
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



        return self.render_json_response(
            authorization = True,
            success = True,
            #servers = servers_response
        )
