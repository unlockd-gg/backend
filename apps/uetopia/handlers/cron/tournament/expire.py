import logging
import datetime
import uuid
import urllib
import json
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

from httplib2 import Http
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.tournament_sponsors import TournamentSponsorsController

from apps.uetopia.controllers.groups import GroupsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class TournamentExpireHandler(BaseHandler):
    def get(self):
        """

        """
        logging.info('Cron Tournament Expire')

        usersController = UsersController()
        gameController = GamesController()
        #mController = MatchController()
        #spmController = ServerPlayerMembersController()
        #mpController = MatchPlayerController()
        #serverController = ServerController()
        #nController = NotificationsController()
        chat_channel_controller = ChatChannelsController()
        transactionController = TransactionsController()
        tournamentController = TournamentsController()
        tournamentSponsorController = TournamentSponsorsController()
        lockController = TransactionLockController()
        teamController = TeamsController()
        groupController = GroupsController()

        tournaments = tournamentController.get_stale_not_completed()

        for tournament in tournaments:
            ## return the additional buy-ins
            logging.info("tournament.additionalPrizeFromHost: %s" % tournament.additionalPrizeFromHost)
            logging.info("tournament.hostUserKeyId: %s" % tournament.hostUserKeyId)

            if tournament.additionalPrizeFromHost > 0:
                logging.info("Returning the host additional buyin")

                host_user = usersController.get_by_key_id(tournament.hostUserKeyId)

                description = "Returned Unclaimed Tournament Prize: %s for %s" %(tournament.title, tournament.additionalPrizeFromHost)
                transactionController.create(
                    amountInt = tournament.additionalPrizeFromHost,
                    description = description,
                    userKeyId = host_user.key.id(),
                    firebaseUser = host_user.firebaseUser,
                    transactionType = "user",
                    transactionClass = "tournament_prize",
                    transactionSender = False,
                    transactionRecipient = True,
                    #recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_TOURNAMENT,
                    materialDisplayClass = "md-primary"
                )
                pushable = lockController.pushable("user:%s"%host_user.key.id())
                if pushable:
                    logging.info('user pushable')
                    taskUrl='/task/user/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": host_user.key.id()
                                                                                    }, countdown=2)


            ## update the tournament
            tournament.completed = True
            tournament.finalized = True
            tournament.unplayedExpired = True

            tournamentController.update(tournament)

            ## get all of the teams and set flags.
            teams_in_tournament = teamController.get_list_by_tournament(tournament.key.id())
            for team_in_tournament in teams_in_tournament:
                team_in_tournament.inTournament = False
                team_in_tournament.nextTournamentStartTime = None
                team_in_tournament.nextTournamentEndTime = None
                team_in_tournament.nextTournamentKeyId = None
                team_in_tournament.nextTournamentTitle = None
                team_in_tournament.nextTournamentEliminated = None
                teamController.update(team_in_tournament)


            ## message all the players and delete the chat channel
            chat_channel = chat_channel_controller.get_by_channel_type_refKeyId("tournament", tournament.key.id())

            ## send a tournament update
            taskUrl='/task/tournament/push'
            taskqueue.add(url=taskUrl, queue_name='tournamentPush', params={'key_id': tournament.key.id()}, countdown=4)

            if chat_channel:
                logging.info('Found a chat channel. messaging then deleting it.')

                ## TODO send a heroku push notifying subscribers that the tournament is expired

                ## send a text chat
                message="Tournament %s expired." %tournament.title
                taskUrl='/task/chat/channel/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': chat_channel.key.id(),
                                                                                    "message": message,
                                                                                    #"userKeyId": authorized_user.key.id(),
                                                                                    #"userTitle": authorized_user.title,
                                                                                    "chatMessageKeyId": uuid.uuid4(),
                                                                                    "chatChannelTitle": chat_channel.title,
                                                                                    "chatChannelRefType":chat_channel.channel_type,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })

                taskUrl='/task/chat/channel/delete'
                taskqueue.add(url=taskUrl, queue_name='chatChannelDelete', params={'key_id': chat_channel.key.id()}, countdown = 3,)


            game = gameController.get_by_key_id(tournament.gameKeyId)

            ## do slack/discord pushes for the game if enabled
            if game.slack_subscribe_new_tournaments and game.slack_webhook:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Tournament Expired: %s | %s" % (tournament.key.id(), tournament.title)
                slack_data = {'text': message}
                data=json.dumps(slack_data)
                resp, content = http_auth.request(game.slack_webhook,
                                  "POST",
                                  data,
                                  headers=headers)

            if game.discord_subscribe_new_tournaments and game.discord_webhook:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Tournament Expired: %s | %s" % (tournament.key.id(), tournament.title)
                #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                discord_data = { "embeds": [{"title": "Tournament Expired", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook,
                                  "POST",
                                  data,
                                  headers=headers)

            ## send a message out to the group if this is a group tournament
            ## changing this around to send to all sponsors

            sponsors = tournamentSponsorController.get_list_by_tournamentKeyId(tournament.key.id())
            for sponsor in sponsors:

            #if tournament.groupKeyId:
                group = groupController.get_by_key_id(sponsor.groupKeyId)
                if group:
                    if group.discord_subscribe_tournaments:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
                        d_message = "%s  %s" % (tournament.title, link)
                        #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                        discord_data = { "embeds": [{"title": "Tournament Expired", "description": d_message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(group.discord_webhook,
                                          "POST",
                                          data,
                                          headers=headers)
                    if group.slack_subscribe_tournaments:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
                        s_message = "Tournament %s expired | %s" % (tournament.title, link)
                        slack_data = {'text': s_message}
                        data=json.dumps(slack_data)
                        resp, content = http_auth.request(group.slack_webhook,
                                          "POST",
                                          data,
                                          headers=headers)

        ## task active list to all
        #taskUrl='/task/all/active/list'
        #taskqueue.add(url=taskUrl, queue_name='taskAllActiveList', countdown=8)
