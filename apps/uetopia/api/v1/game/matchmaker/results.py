import logging
import re
import datetime
import os
import math
import json
import time
import hashlib
import hmac
import urllib
import httplib
import base64
import uuid
from collections import OrderedDict
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
#from apps.uetopia.controllers.game_player_snapshot import GamePlayerSnapshotController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
#from apps.uetopia.controllers.server import ServerController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.server_clusters import ServerClustersController

from apps.uetopia.controllers.match_results import MatchResultsController
from apps.uetopia.controllers.match_results_user import MatchResultsUserController

from apps.uetopia.controllers.match_teams import MatchTeamsController

from apps.uetopia.controllers.server_instances import ServerInstancesController
#from apps.uetopia.controllers.server_player_members import ServerPlayerMembersController
#from apps.uetopia.controllers.award import AwardController
#from apps.uetopia.controllers.event_feed import EventFeedController
#from apps.uetopia.controllers.tournament import TournamentController
#from apps.uetopia.controllers.team import TeamController
#from apps.uetopia.controllers.team_player_members import TeamPlayerMembersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.event_feed import EventFeedController

from apps.uetopia.utilities.game_player_snapshot import create_game_player_snapshot
from apps.uetopia.controllers.game_characters import GameCharactersController

from configuration import *
#from apps.leetcoin.providers.riot import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class PutMatchMakerResutlsHandler(BaseHandler):
    def post(self):
        """
        Post Match Results
        Requires http headers:  Key, Sign
        Requires JSON parameters:  nonce, matchInfo
        """

        mr_controller = MatchResultsController()
        matchController = MatchController()
        mpController = MatchPlayersController()
        gamePlayersController = GamePlayersController()
        #gamePlayerSnapshotController = GamePlayerSnapshotController()
        transactionController = TransactionsController()

        groupGameController = GroupGamesController()

        serverInstancesController = ServerInstancesController()
        gamesController = GamesController()
        serverClusterController = ServerClustersController()
        lockController = TransactionLockController()
        #aController = AwardController()
        #pcontroller = PlayerController()
        #nController = NotificationsController()
        #tournamentController = TournamentController()
        #teamController = TeamController()
        #teamPlayerMembersController = TeamPlayerMembersController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chatMessageController = ChatMessagesController()

        eventFeedController = EventFeedController()
        gameCharacterController = GameCharactersController()

        matchTeamController = MatchTeamsController()

        ## Authenticate the request.
        ## We have an incoming match key signed by a matchKey


        logging.info(self.request)

        try:
            match = matchController.verify_signed_auth(self.request)
        except:
            logging.error("Could not find a match with the supplied key.")
            return self.render_json_response(
                message = "Could not find a match with the supplied key.",
            )



        if match == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            jsonstring = self.request.body
            #logging.info(jsonstring)
            jsonobject = json.loads(jsonstring)


            ### INSERTING FROM task_matchmaker_verify
            ## TODO modularize this.

            match_players = mpController.get_list_by_matchKeyId(match.key.id())
            game = gamesController.get_by_key_id(match.gameKeyId)

            match_validated_complete = False

            ## CHECK TO MAKE SURE THE MATCH HAS NOT ALREADY BEEN VERIFIED

            if match.allPlayersVerified:
                logging.info('This match has already been verified.')
                ## TODO unmute this.
                #return self.render_json_response(
                #    message = "This match has already been verified.",
                #)

            past_date = datetime.datetime.now() - MATCHMAKER_MAXIMUM_VERIFICATION_GRACE_PERIOD

            ## Delete the match chat channel and subscribers
            match_chat_channel = chatChannelController.get_by_channel_type_refKeyId("match", match.key.id())


            ## matches get purged if they are too old, or other failure modes are encountered.

            purge_match = False

            ## Check to make sure the match is not too old

            if match.created < past_date:
                logging.info("match.created < past_date - Purging")
                ## TODO undo this - just testing
                #purge_match = True

            ## TODO any other purge cases?

            if purge_match:
                #We are here because the maximum validation time has expired,
                for match_player in match_players:
                    logging.info("doing post match processing for: %s" %match_player.userKeyId)

                    ## TODO

                ## mark the game as verified

                match.matchVerified = False
                match.allPlayersVerified = False

                ##matchController.update(match)

                ## TODO send a chat notification
                ## TODO send a match update push

                return self.render_json_response(
                    message = "The maximum verification grace period has elapsed.  The match has been invalidated and all deposits returned. ",
                )

            else:
                ## the match does not need to be purged, continue as normal



                all_player_data_json = jsonobject['players']
                #logging.info("all_player_data_json request: %s" %all_player_data_json)
                #logging.info(all_player_data_json)

                ## keep track of the team chat channels that need to get deleted
                team_chat_channel_list = []

                ## does the list of player keys match?
                matching_count = 0
                notmatching = 0
                ## is the team information correct?
                team_info_correct = True

                for i, match_player in enumerate(match_players):
                    logging.info('checking: %s' %match_player.userKeyId)
                    for json_player in all_player_data_json:
                        if str(match_player.userKeyId) == json_player['userKeyId']:
                            logging.info('approved player found')
                            matching_count = matching_count +1
                            match_player.json_index = i
                            if match_player.teamId != json_player['teamId']:
                                logging.info('teamId mismatch')
                                team_info_correct = False

                        else:
                            logging.info('approved player not found')
                            notmatching = notmatching +1

                logging.info("Checking the submitted player list against our records")
                logging.info("matching_count: %s" % matching_count)
                logging.info("len(match_players): %s" % len(match_players))
                logging.info("len(all_player_data_json['players']): %s" % len(all_player_data_json))

                if not len(all_player_data_json) == len(match_players) == matching_count:
                    logging.info('player count mismatch')

                    playercountmismatch = True

                    ## Send discord error and wipe out the game records.
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())
                    headers = {"Content-Type": "application/json"}
                    if game.discord_subscribe_errors and game.discord_webhook_admin:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "The submitted matchmaker results did not match with the expected player count."
                        url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                        discord_data = { "embeds": [{"title": "Matchmaker Results Error", "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)

                    ## nuke the match and the players
                    for match_player in match_players:
                        logging.info("UserKeyID: %s" %match_player.userKeyId)

                        mpController.delete(match_player)

                    matchController.delete(match)



                    return self.render_json_response(
                        message = "Player Count Mismatch. ",
                    )

                if not team_info_correct:
                    logging.info('teamId mismatch')
                    return self.render_json_response(
                        message = "Team ID Mismatch. ",
                    )

                ##########
                ## Copied from api put_match_results

                ## TODO refactor this as a utility

                #aController = AwardController()

                ## Set up our variables

                map_title = 'unused'


                ## Example
                ## playerList = [winner1, winner2. loser1]

                logging.info("Starting post match processing.")

                ## TODO if no rank came back, calculate it

                ## TODO update matchplayer

                winning_team_key = None
                losing_team_key = None
                winning_team_title = None

                ## we need to calculate the game gross, and uetopia percentage rake
                #match.admissionFeePerPlayer
                #match.winRewardPerPlayer

                total_admission_fees_collected = len(match_players) * match.admissionFeePerPlayer
                total_win_rewards_paid = 0

                ## keep track of the winning player's groupKeyId
                ## If all of the members in the team are in the same group, we'll send a push out to the group discord announcing the winner
                winningTeamGroupKeyId = None
                winningTeamIsNOTGroup = False

                ## keep track of the winning team captain's playerKeyId
                ## If it is a metagame match, we need to send it back
                winningTeamCaptainPlayerKeyId = None

                ## We need to handle the matchPlayer record to update statuses
                ## We send out chat messages here too

                for i, match_player in enumerate(match_players):
                    logging.info('Checking matchPlayer: %s' %match_player.userKeyId)


                    ## update the match player also
                    match_player.verified = True
                    match_player.committed = False

                    ## matchmaker stuff
                    #matchmakerStarted = True,
                    match_player.matchmakerPending = False ## this should already be false, but we'll be sure.
                    #matchTaskStatusKeyId = match_task_status.key.id(),
                    #matchmakerFoundMatch = False,
                    #matchmakerServerReady = False,
                    #matchmakerFinished = False,
                    match_player.matchmakerJoinable = False
                    match_player.matchmakerJoinPending = False
                    #matchmakerMode = matchtype,

                    match_player.rank = all_player_data_json[match_player.json_index]['rank']
                    match_player.score = all_player_data_json[match_player.json_index]['score']
                    match_player.win = all_player_data_json[match_player.json_index]['win']
                    match_player.experience = all_player_data_json[match_player.json_index]['experience']




                    chat_message = "> Left match chat"

                    ## get the team chat channel
                    ## this really needs some models :
                    ## Match Team -
                    ## match team member -

                    ## for now as a hack, just using the match key id
                    ## its not going to work becasue there are more matches than just one.
                    ## fuck, just create the models properly


                    if match_player.matchTeamKeyId:
                        logging.info('found matchTeamKeyId')
                        match_team_chat_channel = chatChannelController.get_by_channel_type_refKeyId("matchteam", match_player.matchTeamKeyId)
                        if match_team_chat_channel:
                            logging.info('found match_team_chat_channel')
                            chat_message = chat_message + " and match team chat"
                            ## keep track of it so we can delete it later
                            if not match_team_chat_channel in team_chat_channel_list:
                                team_chat_channel_list.append(match_team_chat_channel)

                            ## this happens in the task, but in this case, we want to do it right away so when the new chat channel list gets sent, these are not included.
                            match_team_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_team_chat_channel.key.id(), match_player.userKeyId )
                            if match_team_chat_channel_subscriber:
                                logging.info('found match_team_chat_channel_subscriber')
                                chatChannelSubscribersController.delete(match_team_chat_channel_subscriber)

                    ##  Send out a text message to the player
                    taskUrl='/task/chat/channel/list_changed'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': match_player.firebaseUser,
                                                                                    'userKeyId': match_player.userKeyId,
                                                                                    'textMessage': chat_message
                                                                                    }, countdown = 2)

                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': match_player.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })


                    ## Send out additional push notifications to the player so that the UI reloads
                    if match_player.teamKeyId:
                        taskUrl='/task/team/firebase/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': match_player.teamKeyId}, countdown = 8,)

                    else:
                        ## push out a team empty message
                        taskUrl='/task/team/update_player_noteam'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebaseUser': match_player.firebaseUser}, countdown = 8,)

                    ## Flag to prevent the stale detection task to find this
                    ## why is this not working sometimes?

                    match_player.stale_requires_check = False
                    mpController.update(match_player)

                    if match_player.win:
                        winning_team_key = match_player.teamKeyId
                        winning_team_title = match_player.teamTitle

                        if match_player.teamCaptain:
                            winningTeamCaptainPlayerKeyId = match_player.gamePlayerKeyId

                        if not winningTeamIsNOTGroup:
                            ## flag to abort has not been set
                            ## keep checking
                            if match_player.groupTagKeyId:
                                logging.info('found groupTagKeyId')
                                if not winningTeamGroupKeyId:
                                    ## the key has not been set yet.
                                    ## set it
                                    logging.info('setting groupTeamKeyId: %s' %match_player.groupTagKeyId)
                                    winningTeamGroupKeyId = match_player.groupTagKeyId
                                else:
                                    ## the key has already been set
                                    ## make sure it matches
                                    if match_player.groupTagKeyId != winningTeamGroupKeyId:
                                        logging.info('group team does not match')
                                        winningTeamIsNOTGroup = True
                            else:
                                winningTeamIsNOTGroup = True


                        ## Don't do transactions for tournaments
                        if not match.tournamentKeyId:
                            total_win_rewards_paid = total_win_rewards_paid + match.winRewardPerPlayer

                            logging.info('creating transactions for winner')
                            # make sure the game has enough balance
                            if game.currencyBalance > match.winRewardPerPlayer:
                                logging.info('game has enough balance')

                                description = "Won Match: %s" %match.title
                                transactionController.create(
                                    amountInt = match.winRewardPerPlayer,
                                    description = description,
                                    userKeyId = match_player.userKeyId,
                                    firebaseUser = match_player.firebaseUser,
                                    transactionType = "user",
                                    transactionClass = "match win",
                                    transactionSender = False,
                                    transactionRecipient = True,
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_MATCH_WIN,
                                    materialDisplayClass = "md-primary"
                                )

                                pushable = lockController.pushable("user:%s"%match_player.userKeyId)
                                if pushable:
                                    logging.info('user pushable')
                                    taskUrl='/task/user/transaction/process'
                                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                        "key_id": match_player.userKeyId
                                                                                                    }, countdown=2)

                                ## Create a transaction for the game
                                description = "Match winner payment"

                                ## Create a transaction for the withdrawl -game
                                transactionGame = TransactionsController().create(
                                    #userKeyId = gamePlayer.userKeyId,
                                    gameKeyId = game.key.id(),
                                    gameTitle = game.title,
                                    #firebaseUser = gamePlayer.firebaseUser,
                                    description = description,
                                    amountInt = -match.winRewardPerPlayer,
                                    newBalanceInt = 0,
                                    #serverPlayerKeyId = server_player.key.id(),
                                    transactionType = "game",
                                    transactionClass = "match win payment",
                                    transactionSender = False,
                                    transactionRecipient = True,
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_MATCH_WIN,
                                    materialDisplayClass = "md-accent"
                                    )
                        else:
                            logging.info('skipping transactions for tournament match')


                        displayText = "Won a match in %s" % game.title

                        ## Add an event to the user event feed
                        eventFeedController.create(
                            #gameKeyId = game.key.id(),
                            #gameTitle = game.title,
                            #gameDisplayText = gameDisplayText,

                            #serverKeyId = server.key.id(),
                            #serverTitle = server.title,
                            #serverDisplayText = gameDisplayText,

                            #matchKeyId = ndb.IntegerProperty()
                            #matchTitle = ndb.StringProperty(indexed=False)
                            #matchDisplayText = ndb.StringProperty(indexed=False)

                            #groupKeyId = groupKeyId,
                            #groupTitle = groupTitle,
                            #groupDisplayText = notGameDisplayText,

                            userKeyId = match_player.userKeyId,
                            userTitle = match_player.userTitle,
                            userDisplayText = displayText,

                            eventType = "match win",

                            ##text =
                            icon = MATERIAL_ICON_MATCH_WIN

                            #value = ndb.IntegerProperty(indexed=False)
                        )

                        taskUrl='/task/user/events/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': match_player.userKeyId}, countdown = 2,)


                    elif match_player.win == False:
                        losing_team_key = match_player.teamKeyId


                    ## update the game player also.
                    game_player = gamePlayersController.get_by_key_id(match_player.gamePlayerKeyId)

                    ## check for characters
                    if game.characters_enabled:
                        logging.info('characters are enabled.')
                        if game_player.characterCurrentKeyId:
                            logging.info('this game_player has a characterCurrentKeyId')
                            game_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
                            if game_character:
                                logging.info('game character found')
                                ## OK to go
                                game_character.rank = all_player_data_json[match_player.json_index]['rank']
                                game_character.score = game_player.score + all_player_data_json[match_player.json_index]['score']
                                if game_character.experience:
                                    game_character.experience = game_character.experience + all_player_data_json[match_player.json_index]['experience']
                                else:
                                    game_character.experience = all_player_data_json[match_player.json_index]['experience']

                                gameCharacterController.update(game_character)
                                character_snapshot = create_game_player_snapshot(game_character, characterKeyId=game_character.key.id())
                        else:
                            logging.info('A character was not selected.')
                    else:
                        logging.info('characters are not enabled')



                        game_player.rank = all_player_data_json[match_player.json_index]['rank']
                        game_player.score = game_player.score + all_player_data_json[match_player.json_index]['score']
                        if game_player.experience:
                            game_player.experience = game_player.experience + all_player_data_json[match_player.json_index]['experience']
                        else:
                            game_player.experience = all_player_data_json[match_player.json_index]['experience']
                        gamePlayersController.update(game_player)

                        ## Create a snapshot
                        ##gamePlayerSnapshotController.create(**game_player.to_dict())
                        snapshot = create_game_player_snapshot(game_player, gamePlayerKeyId=game_player.key.id())

                        taskUrl='/task/game/player/firebase/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game_player.key.id()}, countdown = 2,)


                ## TODO compare winners against what the teams should have been

                ## push out a chat alert to the match chat announcing the winner
                if match_chat_channel:
                    if winning_team_title:
                        text_message = "%s won the match" % winning_team_title
                    else:
                        text_message = "AIs won the match"

                    ## add the message to the database
                    chat_message = chatMessageController.create(
                        chatChannelKeyId = match_chat_channel.key.id(),
                        chatChannelTitle = match_chat_channel.title,
                        text = text_message
                    )
                    ## send the match channel the created message
                    taskUrl='/task/chat/channel/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': match_chat_channel.key.id(),
                                                                                            "message": text_message,
                                                                                            #"playerKey": "SYSTEM",
                                                                                            #"playerTitle": "SYSTEM",
                                                                                            "chatMessageKeyId": chat_message.key.id(),
                                                                                            "chatChannelTitle": match_chat_channel.title,
                                                                                            "chatChannelRefType": match_chat_channel.channel_type
                                                                                        }, countdown=0)

                    taskUrl='/task/chat/channel/delete'
                    taskqueue.add(url=taskUrl, queue_name='chatChannelDelete', params={'key_id': match_chat_channel.key.id()}, countdown = 3,)


                if winning_team_title:
                    gameDisplayText = "%s won a match" % winning_team_title
                else:
                    gameDisplayText = "AIs won a match"

                groupDisplayText = None

                group_game = None
                groupKeyId = None
                groupTitle = None
                ## set vars for group feed
                if not winningTeamIsNOTGroup:
                    logging.info('doing group event')
                    ## make sure the group is connected to the game - we also need the discord channel from here
                    group_game = groupGameController.get_by_groupKeyId_gameKeyId(winningTeamGroupKeyId, match.gameKeyId)
                    if group_game:

                        groupKeyId = winningTeamGroupKeyId
                        groupTitle = group_game.groupTitle
                        if winning_team_title:
                            groupDisplayText = "%s won a match in %s" % (winning_team_title, game.title)
                        else:
                            ## this shouldn't happen, but just in case...
                            groupDisplayText = "AIs won a match in %s" % (game.title)

                ## check to see if there is a server cluser set up to recieve events from this region
                server_cluster = serverClusterController.get_by_gameKeyId_vm_region_mmevents(game.key.id(), match.continuous_server_region)
                if server_cluster:
                    logging.info('found a designated server cluster to recieve MM events in this region.')
                    serverClusterKeyId = server_cluster.key.id()
                    serverClusterTitle = server_cluster.title

                    taskUrl='/task/game/cluster/events/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_cluster.key.id()}, countdown = 2,)

                else:
                    logging.info('did not find a designated server cluster to recieve MM events in this region.')
                    serverClusterKeyId = None
                    serverClusterTitle = None

                ## Add an event to the game event feed
                eventFeedController.create(
                    gameKeyId = game.key.id(),
                    gameTitle = game.title,
                    gameDisplayText = gameDisplayText,

                    #serverKeyId = server.key.id(),
                    #serverTitle = server.title,
                    #serverDisplayText = gameDisplayText,
                    serverClusterKeyId = serverClusterKeyId,
                    serverClusterTitle = serverClusterTitle,

                    #matchKeyId = ndb.IntegerProperty()
                    #matchTitle = ndb.StringProperty(indexed=False)
                    #matchDisplayText = ndb.StringProperty(indexed=False)

                    groupKeyId = groupKeyId,
                    groupTitle = groupTitle,
                    groupDisplayText = groupDisplayText,

                    #userKeyId = server_player.userKeyId,
                    #userTitle = server_player.userTitle,
                    #userDisplayText = notGameDisplayText,

                    eventType = "match win",

                    ##text =
                    icon = MATERIAL_ICON_MATCH_WIN

                    #value = ndb.IntegerProperty(indexed=False)
                )

                taskUrl='/task/game/events/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game.key.id()}, countdown = 2,)

                ## push a notification to the game's discord

                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                headers = {"Content-Type": "application/json"}
                if game.discord_subscribe_match_win and game.discord_webhook:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = gameDisplayText
                    url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Match Winner", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)




                ## Discord push for the group too
                if group_game:
                    ## update firebase with the new event
                    taskUrl='/task/group/events/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': groupKeyId}, countdown = 2,)
                    ## also send a discord push if configured
                    if group_game.discord_subscribe_game_event_feed_wins and group_game.discordWebhook:
                        gamelink = "https://uetopia.com/#/game/" + str(group_game.gameKeyId)
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = groupDisplayText
                        discord_data = { "embeds": [{"title": "Match Win", "url": gamelink, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(group_game.discordWebhook,
                                          "POST",
                                          data,
                                          headers=headers)


                ## Calculate UETOPIA rake -only if not tournament
                if not match.tournamentKeyId:
                    gross_income_from_game = total_admission_fees_collected - total_win_rewards_paid

                    uetopia_rake = int(gross_income_from_game * UETOPIA_GROSS_PERCENTAGE_RAKE)
                    logging.info("uetopia_rake: %s" % uetopia_rake)

                    description = "UETOPIA match rake"

                    ## Create a transaction for the rake withdrawl -game
                    transactionGameRake = TransactionsController().create(
                        #userKeyId = gamePlayer.userKeyId,
                        gameKeyId = game.key.id(),
                        gameTitle = game.title,
                        #firebaseUser = gamePlayer.firebaseUser,
                        description = description,
                        amountInt = -uetopia_rake,
                        newBalanceInt = 0,
                        #serverPlayerKeyId = server_player.key.id(),
                        transactionType = "game",
                        transactionClass = "match income uetopia percentage",
                        transactionSender = False,
                        transactionRecipient = True,
                        submitted = True,
                        processed = False,
                        materialIcon = MATERIAL_ICON_MATCH_WIN,
                        materialDisplayClass = "md-accent"
                        )

                    ## process match transactions
                    pushable = lockController.pushable("game:%s"%game.key.id())
                    if pushable:
                        logging.info('game pushable')
                        taskUrl='/task/game/transaction/process'
                        taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                            "key_id": game.key.id()
                                                                                        }, countdown=2)

                    ## uetopia rake transaction is marked processed - just keeping track of it
                    description = "Match Complete Percentage from: %s" %game.title
                    recipient_transaction = transactionController.create(
                        amountInt = uetopia_rake,
                        description = description,
                        gameKeyId = game.key.id(),
                        gameTitle = game.title,
                        transactionType = "uetopia",
                        transactionClass = "match rake",
                        transactionSender = False,
                        transactionRecipient = True,
                        submitted = True,
                        processed = True,
                        materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                        materialDisplayClass = "md-primary"
                    )

                ## mark the match as verified

                match.matchVerified = True
                match.allPlayersVerified = True

                #match.verifiedMatchId = str(match.key.urlsafe())
                logging.info('winning_team_key %s' %winning_team_key )
                logging.info('losing_team_key %s' %losing_team_key )

                match.tournamentMatchWinnerKeyId = winning_team_key
                match.tournamentMatchLoserKeyId = losing_team_key




                ## check to see if this game is in local testing mode
                if game.match_deploy_vm_local_testing:
                    ## wipe out the apikey and secret so we can reuse them

                    ## This is causing a problem because the results get submitted as soon as the match is over, but the gamePlayer is not saved until
                    ## after the loot is claimed.

                    ## So instead, we need to put this on a task to run later.
                    ## there is a possible issue with local testing if they queue up matches too quickly or something.
                    ## But it is just local so I'm not too concerned.

                    ## start a task to clear the key/secret
                    taskUrl='/task/matchmaker/local_clear_key_secret'

                    taskqueue.add(url=taskUrl, queue_name='matchLocalClearKeySecret', params={'key_id': match.key.id()
                                                                                        }, countdown=MATCHMAKER_WAIT_FOR_LOCAL_KEY_SECRET_CLEAR_DELAY_SECONDS)

                    #match.apiKey = None
                    #match.apiSecret = None
                else:
                    ## deal with the dynamic servers
                    #if match.match_provisioned:
                    logging.info("this is a matchmaker VM")



                    ## start a task to dealoocate the VM
                    taskUrl='/task/matchmaker/vm/deallocate'
                    vmTitle = "m%s" %match.key.id()
                    taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': 'ue4topia',
                                                                                            "zone": match.continuous_server_zone,
                                                                                            "name": vmTitle,
                                                                                            "matchKeyId": match.key.id()
                                                                                        }, countdown=MATCHMAKER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS)

                # make it so that the check unused task will fail

                match.match_active = False
                match.match_provisioned = False
                match.match_creating = False
                #match.continuous_server_creating_timestamp = None
                match.match_destroying = True
                match.match_destroying_timestamp = datetime.datetime.now()
                match.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
                match.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
                match.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value

                ## TODO unmute this just testing
                matchController.update(match)

                ## delete all of the team channels
                for team_chat_channel in team_chat_channel_list:
                    chatChannelController.delete(team_chat_channel)

                ## create a server_instance record.only if this was not localtesting
                if match.continuous_server_zone != 'localtesting':
                    logging.info('found a match that used a VM - adding instance record for processing')
                    created_datetime = match.created

                    destroying_datetime = datetime.datetime.now()
                    total_seconds = (destroying_datetime - created_datetime).total_seconds()
                    if total_seconds < VM_INSTANCE_MINIMUM_SECONDS:
                        total_seconds = VM_INSTANCE_MINIMUM_SECONDS

                    ## round up
                    billable_min_uptime = int((total_seconds+(-total_seconds%60))//60)

                    serverInstance = serverInstancesController.create(
                        #serverKeyId = server.key.id(),
                        #serverTitle = server.title,
                        gameKeyId = match.gameKeyId,
                        gameTitle = match.gameTitle,

                        machine_type = match.continuous_server_machine_type,
                        region_name = match.continuous_server_region,

                        continuous_server_creating_timestamp = created_datetime,
                        continuous_server_destroying_timestamp = destroying_datetime,

                        uptime_minutes_billable = billable_min_uptime,

                        #serverClusterKeyId = server.serverClusterKeyId,
                        ##serverClusterTitle = server.serverClusterTitle,

                        #userKeyId = server.userKeyId,
                        processed = False,
                        instanceType = 'match'
                    )


                ## store match results in the match

                ## deal with match chat cahnnel and it's subscribers


                ## TODO Fire off a task to check on tournament round completion

                if match.tournamentKeyId:
                    logging.info('This match is part of a tournament.  Creating a task to check on round completion.')

                    taskUrl='/task/tournament/round/end'
                    taskqueue.add(url=taskUrl, queue_name='tournamentProcessing', params={'key_id': match.tournamentKeyId}, countdown=2)

                if match.metaMatchKeyId:
                    logging.info('this match is metamode - notifying the endpoint')

                    if game.match_metagame_api_url:
                        logging.info('game match_metagame_api_url is set up')

                        if winningTeamCaptainPlayerKeyId:
                            logging.info('found winningTeamCaptainPlayerKeyId')

                            uri = "/api/v1/metagame/match_results"

                            ## send params as json.
                            json_params = OrderedDict([
                                ("nonce", time.time()),
                                ("match_key_id", match.metaMatchKeyId),
                                ("winning_user_key_id", winningTeamCaptainPlayerKeyId)
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


                            logging.info('the metagame API request was successful')


                return self.render_json_response(
                    authorization = True,

                )
