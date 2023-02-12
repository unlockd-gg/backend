import logging
import re
import datetime
import os
import math
import json

import base64
import uuid
from httplib2 import Http
from apps.handlers import BaseHandler
from google.appengine.api import users
from google.appengine.api import taskqueue
#from google.appengine.ext import deferred
#from google.appengine.api import channel
#from apps.leet.providers.steam import *

from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController

from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
#from apps.uetopia.controllers.server import ServerController

from apps.uetopia.controllers.match_results import MatchResultsController
from apps.uetopia.controllers.match_results_user import MatchResultsUserController

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_instances import ServerInstancesController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.group_games import GroupGamesController
#from apps.uetopia.controllers.award import AwardController
#from apps.uetopia.controllers.event_feed import EventFeedController
#from apps.uetopia.controllers.tournament import TournamentController
#from apps.uetopia.controllers.team import TeamController
#from apps.uetopia.controllers.team_player_members import TeamPlayerMembersController

from apps.uetopia.controllers.event_feed import EventFeedController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *
#from apps.leetcoin.providers.riot import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class PutMatchResultsHandler(BaseHandler):
    def post(self):
        """
        Post Match Results
        Requires http headers:  Key, Sign
        Requires JSON parameters:  nonce, matchInfo
        """

        userController = UsersController()
        mr_controller = MatchResultsController()
        matchResultsUserController = MatchResultsUserController()
        matchController = MatchController()
        mpController = MatchPlayersController()
        gamePlayersController = GamePlayersController()
        transactionController = TransactionsController()

        serverInstancesController = ServerInstancesController()
        gamesController = GamesController()
        lockController = TransactionLockController()
        groupGameController = GroupGamesController()
        #aController = AwardController()
        #pcontroller = PlayerController()
        #nController = NotificationsController()
        #tournamentController = TournamentController()
        #teamController = TeamController()
        #teamPlayerMembersController = TeamPlayerMembersController()
        eventFeedController = EventFeedController()

        serverController = ServersController()
        spController = ServerPlayersController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chatMessageController = ChatMessagesController()

        ## Authenticate the request.
        ## We have an incoming match key signed by a matchKey


        logging.info(self.request)

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            logging.error("Could not find a server with the supplied key.")
            return self.render_json_response(
                message = "Could not find a server with the supplied key.",
            )



        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            logging.info("server.gameKeyId: %s" %server.gameKeyId)
            logging.info("server.gameTitle: %s" %server.gameTitle)
            logging.info("server.title: %s" %server.title)

            jsonstring = self.request.body
            #logging.info(jsonstring)
            jsonobject = json.loads(jsonstring)

            players_to_kick = []

            map_title = "unused"

            match_results = mr_controller.create(
                gameKeyId = server.gameKeyId,
                gameTitle = server.gameTitle,
                serverKeyId = server.key.id(),
                serverTitle = server.title,
                mapTitle = map_title
                )

            all_player_data_json = jsonobject['activePlayers']
            logging.info("all_player_data_json request: %s" %all_player_data_json)
            #logging.info(all_player_data_json)

            logging.info("all_player_data_json len: %s" %len(all_player_data_json))

            # keep track of which pushes we need to handle
            pushEventFeedGame = False

            pushEventFeedServer = False


            for player_data_json in all_player_data_json:
                logging.info("Player data")
                ## get the server player

                server_player = spController.get_server_user(server.key.id(), int(player_data_json['playerKeyId']))

                if server_player:
                    logging.info("Server Player Found")

                    pushEventFeedUser = False
                    pushEventFeedGroup = False

                    if server_player.pending_deauthorize:
                        ## This player needs to get kicked.
                        if not player_data_json['playerKeyId'] in players_to_kick:
                            players_to_kick.append(player_data_json['playerKeyId'])

                    if not server_player.authorized:
                        ## This player needs to get kicked.
                        if not player_data_json['playerKeyId'] in players_to_kick:
                            players_to_kick.append(player_data_json['playerKeyId'])

                    ## Set the rank
                    try:
                        rank = int(player_data_json['rank'])
                    except:
                        rank = 1600
                    server_player.ladderRank = rank

                    if player_data_json['experience']:
                        ## update experience and experience total
                        if not server_player.experience:
                            server_player.experience = 0
                            server_player.experience_total = 0

                        server_player.experience = server_player.experience + int(player_data_json['experience'])
                        server_player.experience_total = server_player.experience_total + int(player_data_json['experience'])


                    ## TODO bounties

                    spController.update(server_player)

                    ## check to see if the user is still wtihin the server hold minimum
                    if server_player.currencyCurrent < server.minimumCurrencyHold:
                        logging.info("player currency is less than the server minimum")
                        if not player_data_json['playerKeyId'] in players_to_kick:
                            players_to_kick.append(player_data_json['playerKeyId'])


                    ## TODO playstyles

                    playerskilled = []
                    playerIdsKilled = []
                    for playerKilled in player_data_json['killed']:
                        logging.info("playerKilled: %s" %playerKilled)
                        ## get the player killed
                        killed_server_player = spController.get_server_user(server.key.id(), int(playerKilled))
                        playerskilled.append(killed_server_player.userTitle)
                        playerIdsKilled.append(int(playerKilled))

                    playerUserRecord = userController.get_by_key_id(server_player.userKeyId)

                    groupKeyId = None
                    groupTitle = None

                    if playerUserRecord.groupTagKeyId:
                        ## make sure the group is connected to the game - we also need the discord channel from here
                        group_game = groupGameController.get_by_groupKeyId_gameKeyId(playerUserRecord.groupTagKeyId, server.gameKeyId)
                        if group_game:
                            groupKeyId = playerUserRecord.groupTagKeyId
                            groupTitle = playerUserRecord.groupTag

                    ## create event feed records
                    raw_event_texts = []
                    for event_record in player_data_json['events']:

                        gameDisplayText = server_player.userTitle  + " " + event_record['eventSummary']
                        notGameDisplayText = server_player.userTitle  + " " + event_record['eventSummary'] + " in " + server.gameTitle

                        raw_event_texts.append(event_record['eventSummary'])

                        eventFeedController.create(
                            gameKeyId = server.gameKeyId,
                            gameTitle = server.gameTitle,
                            gameDisplayText = gameDisplayText,

                            serverKeyId = server.key.id(),
                            serverTitle = server.title,
                            serverDisplayText = gameDisplayText,

                            #matchKeyId = ndb.IntegerProperty()
                            #matchTitle = ndb.StringProperty(indexed=False)
                            #matchDisplayText = ndb.StringProperty(indexed=False)

                            groupKeyId = groupKeyId,
                            groupTitle = groupTitle,
                            groupDisplayText = notGameDisplayText,

                            userKeyId = server_player.userKeyId,
                            userTitle = server_player.userTitle,
                            userDisplayText = notGameDisplayText,

                            eventType = event_record['eventType'],

                            ##text =
                            icon = event_record['eventIcon']

                            #value = ndb.IntegerProperty(indexed=False)
                        )

                        pushEventFeedUser = True
                        pushEventFeedGame = True
                        pushEventFeedServer = True

                        if groupKeyId:
                            pushEventFeedGroup = True

                            ## also send a discord push if configured
                            if group_game.discord_subscribe_game_event_feed_kills and group_game.discordWebhook:
                                gamelink = "https://uetopia.com/#/game/" + str(group_game.gameKeyId)
                                http_auth = Http()
                                headers = {"Content-Type": "application/json"}
                                message = notGameDisplayText
                                discord_data = { "embeds": [{"title": event_record['eventType'], "url": gamelink, "description": message}] }
                                data=json.dumps(discord_data)
                                resp, content = http_auth.request(group_game.discordWebhook,
                                                  "POST",
                                                  data,
                                                  headers=headers)




                    matchResultsUserController.create(
                        gameKeyId = server.gameKeyId,
                        gameTitle = server.gameTitle,
                        serverKeyId = server.key.id(),
                        serverTitle = server.title,
                        matchResultsKeyId = match_results.key.id(),

                        userKeyId = server_player.userKeyId,
                        userName = server_player.userTitle,
                        experience = int(player_data_json['experience']),
                        score = int(player_data_json['score']),
                        rank = int(player_data_json['rank']),
                        #playstyle_killer = int(playstyles[0]),
                        #playstyle_achiever = int(playstyles[1]),
                        #playstyle_explorer = int(playstyles[2]),
                        #playstyle_socializer = int(playstyles[3]),
                        #weapon = player_data_json['weapon'],
                        postiveCount = player_data_json['roundKills'],
                        negativeCount = player_data_json['roundDeaths'],
                        #killedPlayerPlatformID = player_data_json['killed']
                        killedUserKeyIds = playerIdsKilled,
                        killedUserTitles = playerskilled,
                        events = raw_event_texts
                    )

                    ## event feed

                    if pushEventFeedUser:
                        taskUrl='/task/user/events/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.userKeyId}, countdown = 2,)

                    if pushEventFeedGroup:
                        taskUrl='/task/group/events/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': groupKeyId}, countdown = 2,)

                else:
                    logging.info('No serverplayerrecord could be found.  ')
                    ## This player needs to get kicked.
                    if not player_data_json['playerKeyId'] in players_to_kick:
                        players_to_kick.append(player_data_json['playerKeyId'])

            ## check event feeds and handle

            if pushEventFeedGame:
                taskUrl='/task/game/events/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server.gameKeyId}, countdown = 2,)



            return self.render_json_response(
                authorization = True,

            )
