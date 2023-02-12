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


class TaskTournamentEndRound(BaseHandler):
    """
    Start a tournament round

    """
    def post(self):
        """

        """

        logging.info('TaskTournamentEndRound')

        userController = UsersController()
        mpController = MatchPlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        tournamentController = TournamentsController()
        teamController = TeamsController()
        teamMembersController = TeamMembersController()
        gameModeController = GameModesController()


        gcontroller = GamesController()
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

        ## get chat channel for this match
        chat_channel = chatChannelController.get_by_channel_type_refKeyId("tournament", tournament.key.id())
        if not chat_channel:
            logging.error('chat channel not found for tournament')
            return

        ## check to see if all matches in this round are completed.
        matches = mController.get_matches_by_tournamentKeyId_tournamentTier(tournament.key.id(), tournament.current_round)

        completed_count = 0
        for match in matches:
            if match.matchVerified == True:
                completed_count = completed_count +1

        logging.info("completed count: %s" % completed_count)
        logging.info("len(matches): %s" % len(matches))

        if completed_count != len(matches):
            logging.info('not all matches complete')
            return

        ## get all of the remaining teams
        remaining_teams = teamController.get_list_by_tournament_not_eliminated(tournament.key.id())

        ## eliminate the teams that lost
        ## TODO allow for different tournament types here
        logging.info('eliminating losers')

        for match in matches:
            logging.info('checking match')
            if match.tournamentMatchLoserKeyId: ## just make sure it's actually set
                logging.info('tournamentMatchLoserKeyId is set')
                for remaining_team in remaining_teams:
                    if remaining_team.key.id() == match.tournamentMatchLoserKeyId:
                        logging.info('Found match loser: %s' %remaining_team.title)
                        remaining_team.nextTournamentEliminated = True
                        remaining_team.inTournament = False

                        ## TODO do we need to do any kind of processing on match players here?
                        ## Thinking that it all got handled already in other states - check this out.

                        teamController.update(remaining_team)

        logging.info('counting the remaining teams')
        non_eliminated_teams = 0
        for remaining_team in remaining_teams:
            if not remaining_team.nextTournamentEliminated:
                non_eliminated_teams = non_eliminated_teams +1

        logging.info('non_eliminated_teams: %s' %non_eliminated_teams)

        if non_eliminated_teams > 1:
            ## if so, start a new round
            logging.info('Starting the next round.')
            taskUrl='/task/tournament/round/start'
            taskqueue.add(url=taskUrl, queue_name='tournamentProcessing', params={'key_id': tournament.key.id()}, countdown = 2,)
        else:
            ## if not, start a new task to finalize the tournament
            ## TODO Finalize
            logging.info('Starting finalize task')

            taskUrl='/task/tournament/finalize'
            taskqueue.add(url=taskUrl, queue_name='tournamentProcessing', params={'key_id': tournament.key.id()}, countdown = 2,)


        ## alerts and pushes
        ## message out to the tournament chat channel

        ## get chat channel for this tournament
        chat_channel = chatChannelController.get_by_channel_type_refKeyId("tournament", tournament.key.id())
        if not chat_channel:
            logging.error('chat channel not found for tournament')
            return


        message = "Tournament Round %s Complete" %(tournament.current_round)
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
