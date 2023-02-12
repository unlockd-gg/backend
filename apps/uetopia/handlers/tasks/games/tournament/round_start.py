import endpoints
import logging
import uuid
import urllib
import datetime
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor

import google.oauth2.id_token
import google.auth.transport.requests
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
import requests_toolbelt.adapters.appengine

from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

#from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.providers.compute_engine_zonemap import region_zone_mapper

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class TaskTournamentStartRound(BaseHandler):
    """
    Start a tournament round

    """
    def post(self):
        """

        """

        logging.info('TaskTournamentStartRound')

        userController = UsersController()
        mpController = MatchPlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        tournamentController = TournamentsController()
        teamController = TeamsController()
        teamMembersController = TeamMembersController()
        gameModeController = GameModesController()


        gcontroller = GamesController()
        gpController = GamePlayersController()
        mController = MatchController()
        mpController = MatchPlayersController()
        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        chatMessageController = ChatMessagesController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()

        key_id = self.request.get('key_id')

        tournament = tournamentController.get_by_key_id(int(key_id))
        game = gcontroller.get_by_key_id(tournament.gameKeyId)

        tournament.current_round = tournament.current_round + 1

        ## get chat channel for this tournament
        chat_channel = chatChannelController.get_by_channel_type_refKeyId("tournament", tournament.key.id())
        if not chat_channel:
            logging.error('chat channel not found for tournament')
            return

        ## get the game mode we're using
        game_mode = gameModeController.get_by_key_id(tournament.gameModeKeyId)
        if not game_mode:
            logging.error("game mode not found")
            return

        remaining_teams = teamController.get_list_by_tournament_not_eliminated(int(key_id))

        ## TODO some kind of randomization or seeeding on the list results.

        ## allocate servers for each of the matches in the first round
        ## determine if we have even teams
        remainder = len(remaining_teams) %2
        ## set up the first round
        round_team_count = len(remaining_teams) - remainder
        round_match_count = round_team_count/2

        logging.info("round_team_count: %s" %round_team_count)
        logging.info("round_match_count: %s" %round_match_count)

        teamindex = 0

        for i in range(0, round_match_count):
            logging.info("Creating match: %s" % i)
            tournamentTeamKey1 = remaining_teams[teamindex].key.id()
            tournamentTeamTitle1 = remaining_teams[teamindex].title
            teamindex = teamindex +1
            tournamentTeamKey2 = remaining_teams[teamindex].key.id()
            tournamentTeamTitle2 = remaining_teams[teamindex].title
            teamindex = teamindex +1

            match_title = "%s %s:%s" %(tournament.title, tournament.current_round, i)

            ## build all the database records


            """
            ## get the developer if it exists.  WHY?

            developer = DeveloperController().get_by_key(game.developerKey)
            if not developer:
                logging.info('Developer Not Found for this game.')
                developerSecret=""
                developerPlayerKey="agpzfjEzMzdjb2luchMLEgZQbGF5ZXIYgICAgMCljwkM"
                developerKey="agpzfjEzMzdjb2luchYLEglEZXZlbG9wZXIYgICAgMGttAoM"
            else:
                developerSecret = developer.apiSecret
                developerPlayerKey = developer.playerKey
                developerKey = developer.key.urlsafe()



            ## Create a server for this match
            ## FOR NOW HARDCODING THIS.
            ## Keep Current with API manually

            server = serverController.create(
                title = match_title,
                #hostAddress = hostConnectionLink,
                hostPort = "",
                #hostConnectionLink = hostConnectionLink,
                gameKey = game.key.urlsafe(),
                gameTitle = game.title,
                #groupKey = groupKey,
                #groupTitle = groupTitle,
                averageRating = 1,
                averageHonesty = 1,
                maxActivePlayers = tournament.teamSize*2,
                maxAuthorizedPlayers = tournament.teamSize*2,
                developerKey = developerKey,
                platformKey = game.platformKey,
                platformName = game.platformName,
                minimumBTCHold = 0,
                totalBTCHeld = 0,
                incrementBTC = 0,
                bitcoinAwarded = 0,
                apiKey = serverController.create_unique_api_key(),
                apiSecret = serverController.key_generator(),
                serverRakeBTCPercentage = MM_LEETCOIN_SERVER_RAKE,
                serverRakeBTCTotal = 0,
                serverRakeBTCCurrent = 0,
                serverAdminUserKey = developerPlayerKey,
                leetcoinRakePercentage = MM_LEETCOIN_RAKE,
                leetcoinRakeTotal = 0,
                serverInfoRefreshNeeded = False,
                invisible = True,
                internal_matchmaker = True,
                no_death_penalty = False,
                allow_non_authorized_players = False,
                stakesClass = "tournament",
                motdShowBanner = False,
                motdBannerColor = "0",
                motdBannerText  = 'Tournament',
                matchmaker_dynamic_server = matchmaker_dynamic_server,
                matchmaker_dynamic_server_active = matchmaker_dynamic_server, # if its a dynamic server set the active flag to true right away
                ## Grabbing dynamic server details from game.
                ## TODO come up with a way to deal with server configuration templates so they can be user selected.
                dynamic_server_zone = game.dynamic_server_zone,
                dynamic_server_source_disk_image = game.dynamic_server_source_disk_image,
                dynamic_server_machine_type = game.dynamic_server_machine_type,
                dynamic_server_startup_script_location = game.dynamic_server_startup_script_location,
            )

            key = server.key.urlsafe() ## for copy/pasta compatability

            gameJoinLink = game_provider.get_game_join_link(game, mapConfiguration, tournament.teamSize, match_title)
            logging.info("gameJoinLink: %s" % gameJoinLink)

            """

            if game.match_deploy_vm_local_testing:
                logging.info('game is set to local testing mode')

                match = mController.create(
                    title = match_title,
                    gameKeyId = game.key.id(),
                    gameTitle = game.title,
                    playersPerTeam = game_mode.playersPerTeam,
                    teams = game_mode.teams,

                    apiKey = game.match_deploy_vm_local_APIKey,
                    apiSecret = game.match_deploy_vm_local_APISecret,
                    hostConnectionLink = game.match_deploy_vm_local_testing_connection_string,
                    admissionFee = 0,
                    gameModeKeyId = game_mode.key.id(),
                    gameModeTitle = game_mode.onlineSubsystemReference,
                    ## TODO add match initialization settings

                    continuous_server_region = tournament.region,
                    continuous_server_zone = region_zone_mapper(tournament.region),
                    continuous_server_machine_type = game.match_deploy_vm_machine_type,
                    admissionFeePerPlayer = 0, ## for tournaments these get calculated at the end
                    winRewardPerPlayer = 0,## for tournaments these get calculated at the end

                    tournamentKeyId = tournament.key.id(),
                    tournamentTitle = tournament.title,
                    tournamentTier = tournament.current_round,
                    tournamentMatchNumber = i,

                    tournamentTeamKeyId1 = tournamentTeamKey1,
                    tournamentTeamTitle1 = tournamentTeamTitle1,
                    tournamentTeamKeyId2 = tournamentTeamKey2,
                    tournamentTeamTitle2 = tournamentTeamTitle2,

                    allPlayersJoined = False,
                    allPlayersCommitted = False,
                    allPlayersApproved = False,
                    allPlayersLeft = False,
                    allPlayersVerified = False,
                    allPlayersReportedFailure = False,
                    matchExpired = False,
                    matchVerified = False,
                )
            else:
                logging.info('game is set to deploy live VMs')

                match = mController.create(
                    title = match_title,
                    gameKeyId = game.key.id(),
                    gameTitle = game.title,
                    playersPerTeam = game_mode.playersPerTeam,
                    teams = game_mode.teams,

                    apiKey = mController.create_unique_api_key(),
                    apiSecret = mController.key_generator(),
                    admissionFee = 0,
                    gameModeKeyId = game_mode.key.id(),
                    gameModeTitle = game_mode.onlineSubsystemReference,
                    ## TODO add match initialization settings

                    continuous_server_region = tournament.region,
                    continuous_server_zone = region_zone_mapper(tournament.region),
                    continuous_server_machine_type = game.match_deploy_vm_machine_type,
                    admissionFeePerPlayer = 0, ## for tournaments these get calculated at the end
                    winRewardPerPlayer = 0,## for tournaments these get calculated at the end

                    tournamentKeyId = tournament.key.id(),
                    tournamentTitle = tournament.title,
                    tournamentTier = tournament.current_round,
                    tournamentMatchNumber = i,

                    tournamentTeamKeyId1 = tournamentTeamKey1,
                    tournamentTeamTitle1 = tournamentTeamTitle1,
                    tournamentTeamKeyId2 = tournamentTeamKey2,
                    tournamentTeamTitle2 = tournamentTeamTitle2,

                    allPlayersJoined = False,
                    allPlayersCommitted = False,
                    allPlayersApproved = False,
                    allPlayersLeft = False,
                    allPlayersVerified = False,
                    allPlayersReportedFailure = False,
                    matchExpired = False,
                    matchVerified = False,
                )

                ## TODO do we need any checks here?
                ## start a task to create the vm

                ## temporarily muting this
                taskUrl='/task/matchmaker/vm/allocate'
                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                        "matchKeyId": match.key.id()
                                                                                    })

            ## Create the chat channel

            match_chat_title = "match chat"
            match_chat_channel = chatChannelController.create(
                title = match_chat_title,
                channel_type = 'match',
                #adminUserKeyId = authorized_user.key.id(),
                refKeyId = match.key.id(),
                gameKeyId = game.key.id(),
                max_subscribers = 200
            )


            ## create match_players for all members of both teams
            team1_members = teamMembersController.get_by_teamKeyId(tournamentTeamKey1)
            team2_members = teamMembersController.get_by_teamKeyId(tournamentTeamKey2)
            all_team_members = team1_members + team2_members

            for team_member in all_team_members:

                team_member_user_record = userController.get_by_key_id(team_member.userKeyId)
                team_member_game_player = gpController.get_by_gameKeyId_userKeyId(game.key.id(), team_member.userKeyId)

                if team_member.teamKeyId == tournamentTeamKey1:
                    teamId = 0
                else:
                    teamId = 1

                match_player = mpController.create(
                    userKeyId = team_member_user_record.key.id(),
                    userTitle = team_member_user_record.title,
                    firebaseUser = team_member_user_record.firebaseUser,
                    gameKeyId = game.key.id(),
                    teamKeyId = team_member.teamKeyId,
                    teamId = teamId,
                    teamTitle = team_member.teamTitle,
                    matchKeyId = match.key.id(),
                    matchTitle = match.title,

                    ## TODO - identify the flags we're not using and delete them.
                    joined = False,
                    committed = False,
                    approved = False,
                    left = False,
                    verified = False,
                    blocked = False,

                    ## matchmaker stuff
                    matchmakerStarted = True,
                    matchmakerPending = True,
                    #matchTaskStatusKeyId = match_task_status.key.id(),
                    matchmakerFoundMatch = False,
                    matchmakerServerReady = False,
                    matchmakerFinished = False,
                    matchmakerJoinable = False,
                    matchmakerJoinPending = True,
                    matchmakerMode = game_mode.onlineSubsystemReference,  # I think this is legacy/unused.  we use game mode now.

                    rank = team_member_game_player.rank,
                    score = team_member_game_player.score,
                    gamePlayerKeyId = team_member_game_player.key.id()
                )

                ## subscribe the player to the match chat
                subscriber = chatChannelSubscribersController.create(
                    online = True,
                    chatChannelKeyId = match_chat_channel.key.id(),
                    chatChannelTitle = match_chat_channel.title,
                    userKeyId = team_member_user_record.key.id(),
                    userTitle = team_member_user_record.title,
                    userFirebaseUser = team_member_user_record.firebaseUser,
                    post_count = 0,
                    chatChannelRefKeyId = match.key.id(),
                    channel_type = 'match',
                    #chatChannelOwnerKeyId = authorized_user.key.id()
                )

                ## We don't need match team channel, because they should already be in a party chat.


                ## send the user the updated chat channels
                taskUrl='/task/chat/channel/list_changed'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': team_member_user_record.firebaseUser,
                                                                                'userKeyId': team_member_user_record.key.id(),
                                                                                'textMessage': "Chat channel list changed"
                                                                                }, countdown = 2)

                ## we need to fire a matchmaker started task here
                push_payload = {'matchType': 'tournament match'}

                payload_json = json.dumps(push_payload)

                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                headers = {"Content-Type": "application/json"}


                #try:
                URL = "%s/user/%s/matchmaker/started" % (HEROKU_SOCKETIO_SERVER, team_member_user_record.firebaseUser)
                resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      payload_json,
                                      headers=headers)

                logging.info(resp)
                logging.info(content)


            message = "Tournament match created: %s" %(match.title)

            chat_message = chatMessageController.create(
                chatChannelKeyId = match_chat_channel.key.id(),
                chatChannelTitle = match_chat_channel.title,
                #userKeyId = authorized_user.key.id(),
                #userTitle = authorized_user.title,
                text = message,
                #pulled = False
            )

            taskUrl='/task/chat/channel/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': match_chat_channel.key.id(),
                                                                                "message": message,
                                                                                #"userKeyId": authorized_user.key.id(),
                                                                                #"userTitle": authorized_user.title,
                                                                                "chatMessageKeyId": chat_message.key.id(),
                                                                                "chatChannelTitle": match_chat_channel.title,
                                                                                "chatChannelRefType":match_chat_channel.channel_type,
                                                                                "created":chat_message.created.isoformat()
                                                                            }, countdown = 2)



            ## push the match
            #taskUrl='/task/match/push'
            #taskqueue.add(url=taskUrl, queue_name='matchmakerPush', params={'key': match.key.urlsafe()}, countdown = 2,)

            ## start the timer for the match
            ## TODO determine if we still need this
            #taskUrl='/task/match/timer/chat'
            #taskqueue.add(url=taskUrl, queue_name='matchmakerTimerChat', params={'key': match.key.urlsafe(), 'minutes': 10}, countdown = 15,)


        tournament.playStarted = True

        tournamentController.update(tournament)

        ## alerts and pushes
        ## message out to the tournament chat channel

        message = "Tournament Round %s  Fight!" %(tournament.current_round)
        ## add the message to the database
        chat_message = chatMessageController.create(
            chatChannelKeyId = chat_channel.key.id(),
            chatChannelTitle = chat_channel.title,
            text = message
        )
        ## send the match channel the created message
        taskUrl='/task/chat/channel/send'
        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': chat_channel.key.id(),
                                                                                "message": message,
                                                                                #"playerKey": "SYSTEM",
                                                                                #"playerTitle": "SYSTEM",
                                                                                "chatMessageKeyId": chat_message.key.id(),
                                                                                "chatChannelTitle": chat_channel.title,
                                                                                "chatChannelRefType": chat_channel.channel_type
                                                                            }, countdown=2)

        taskUrl='/task/tournament/push'
        taskqueue.add(url=taskUrl, queue_name='tournamentPush', params={'key_id': tournament.key.id()}, countdown = 2,)

        """
        if tournament.current_round == 1:
            ## send everyone the new active list
            taskUrl='/task/all/active/list'
            taskqueue.add(url=taskUrl, queue_name='taskAllActiveList', countdown = 2,)
        """

        ## do slack/discord pushes if enabled
        if game.slack_subscribe_tournament_rounds and game.slack_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Tournament %s Round %s Starting" % (tournament.title, tournament.current_round)
            slack_data = {'text': message}
            data=json.dumps(slack_data)
            resp, content = http_auth.request(game.slack_webhook,
                              "POST",
                              data,
                              headers=headers)

        if game.discord_subscribe_tournament_rounds and game.discord_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message =  "Tournament %s Round %s Starting" % (tournament.title, tournament.current_round)
            #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
            discord_data = { "embeds": [{"title": "Tournament Round Starting", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook,
                              "POST",
                              data,
                              headers=headers)

        ## kick off a new task to monitor this round?
