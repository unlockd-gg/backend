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
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
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

from apps.uetopia.controllers.groups import GroupsController

from apps.uetopia.providers.compute_engine_zonemap import region_zone_mapper

from configuration import *

class TaskTournamentFinalize(BaseHandler):
    """
    Finalize a tournament

    """
    def post(self):
        """

        """

        logging.info('TaskTournamentFinalize')

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

        groupController = GroupsController()

        key_id = self.request.get('key_id')

        tournament = tournamentController.get_by_key_id(int(key_id))
        game = gcontroller.get_by_key_id(tournament.gameKeyId)

        ## get chat channel for this tournament
        chat_channel = chatChannelController.get_by_channel_type_refKeyId("tournament", tournament.key.id())
        if not chat_channel:
            logging.error('chat channel not found for tournament')
            return

        ## get the remaining teams - this should just be the winner.
        remaining_teams = teamController.get_list_by_tournament_not_eliminated(int(key_id))

        ## get all of the teams
        all_teams = teamController.get_list_by_tournament(int(key_id))

        logging.info('len(remaining_teams): %s' %len(remaining_teams))

        if len(remaining_teams) > 1:
            logging.error("Finalize task running but there is not a winner")
            return


        ## update the player records for the winning team
        ## deal with server players and match players?

        ## get team player connections
        winning_team_players = teamMembersController.get_by_teamKeyId(remaining_teams[0].key.id())

        ## figure out the winnings
        ## TODO get tournament doantions

        total_winnings = tournament.estimatedTotalWinnings

        winning_player_count = len(winning_team_players)

        winnings_per_team_member = total_winnings/winning_player_count

        for w_team_player in winning_team_players:
            ## grab the user record
            w_team_player_user = userController.get_by_key_id(w_team_player.userKeyId)

            ## make a transaction
            description = "Tournament Win Payout: %s for %s" %(tournament.title, winnings_per_team_member)
            recipient_transaction = transactionController.create(
                amountInt = winnings_per_team_member,
                ##amount = ndb.FloatProperty(indexed=False) # for display
                ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                ##newBalance = ndb.FloatProperty(indexed=False) # for display
                description = description,
                userKeyId = w_team_player_user.key.id(),
                firebaseUser = w_team_player_user.firebaseUser,
                ##targetUserKeyId = ndb.IntegerProperty()
                ##serverKeyId = server.key.id(),
                ##serverTitle = server.title,

                ##  transactions are batched and processed all at once.
                transactionType = "user",
                transactionClass = "tournament_winnings",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_TOURNAMENT,
                materialDisplayClass = "md-primary"
            )

            ## only start pushable tasks.  If they are not pushable, there is already a task running.
            pushable = lockController.pushable("user:%s"%w_team_player_user.key.id())
            if pushable:
                logging.info('targetUser pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": w_team_player_user.key.id()
                                                                                    }, countdown=2)



        ## calculate uetopia rake
        remaining_currency = tournament.currencyBalance - tournament.estimatedTotalWinnings
        logging.info("remaining_currency: %s" %remaining_currency)

        uetopia_rake = int(remaining_currency * UETOPIA_GROSS_PERCENTAGE_RAKE)
        logging.info("uetopia_rake: %s" % uetopia_rake)

        remaining_amount_to_game = remaining_currency - uetopia_rake
        logging.info("remaining_amount_to_game: %s" % remaining_amount_to_game)

        ## send the remaining cred to the game wallet


        description = "Tournament proceeds from: %s" %tournament.title
        game_transaction = transactionController.create(
            amountInt = remaining_amount_to_game,
            amountIntGross = remaining_currency,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            ##userKeyId = authorized_user.key.id(),
            ##firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            gameKeyId = game.key.id(),
            gameTitle = game.title,

            ##  transactions are batched and processed all at once.
            transactionType = "game",
            transactionClass = "tournament_proceeds",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-primary"
        )

        ## only start pushable tasks.  If they are not pushable, there is already a task running.
        pushable = lockController.pushable("game:%s"%game.key.id())
        if pushable:
            logging.info('game pushable')
            taskUrl='/task/game/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                    "key_id": game.key.id()
                                                                                }, countdown=2)

        ## uetopia rake transaction is marked processed - just keeping track of it
        description = "Tournament Percentage from: %s" %game.title
        recipient_transaction = transactionController.create(
            amountInt = uetopia_rake,
            description = description,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            transactionType = "uetopia",
            transactionClass = "tournament rake",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = True,
            materialIcon = MATERIAL_ICON_ADMISSION_FEE,
            materialDisplayClass = "md-primary"
        )

        tournament.playFinished = True
        tournament.completed = True
        tournament.finalized = True
        tournament.resultDisplayText = "%s won %s!"%(remaining_teams[0].title, total_winnings)
        tournament.currencyBalance = 0
        tournament.estimatedTotalWinnings = 0

        tournamentController.update(tournament)

        ## free up the winning team so they can disband or join a new tournament
        remaining_teams[0].inTournament = False
        teamController.update(remaining_teams[0])

        ## notifications and pushes

        message = "%s won tournament %s" %(remaining_teams[0].title, tournament.title)

        chat_message = chatMessageController.create(
            chatChannelKeyId = chat_channel.key.id(),
            chatChannelTitle = chat_channel.title,
            #userKeyId = authorized_user.key.id(),
            #userTitle = authorized_user.title,
            text = message,
            #pulled = False
        )

        taskUrl='/task/chat/channel/send'
        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': chat_channel.key.id(),
                                                                            "message": message,
                                                                            #"userKeyId": authorized_user.key.id(),
                                                                            #"userTitle": authorized_user.title,
                                                                            "chatMessageKeyId": chat_message.key.id(),
                                                                            "chatChannelTitle": chat_channel.title,
                                                                            "chatChannelRefType": chat_channel.channel_type,
                                                                            "created":chat_message.created.isoformat()
                                                                        }, countdown = 2)

        ## do slack/discord pushes if enabled
        if game.slack_subscribe_new_tournaments and game.slack_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            #message = message
            slack_data = {'text': message}
            data=json.dumps(slack_data)
            resp, content = http_auth.request(game.slack_webhook,
                              "POST",
                              data,
                              headers=headers)

        if game.discord_subscribe_new_tournaments and game.discord_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            #message =  message
            #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
            discord_data = { "embeds": [{"title": "Tournament Winner", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook,
                              "POST",
                              data,
                              headers=headers)

        ## send a message out to the group if this is a group tournament
        if tournament.groupKeyId:
            group = groupController.get_by_key_id(tournament.groupKeyId)
            if group:
                if group.discord_subscribe_tournaments and group.discord_webhook:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
                    d_message = "%s  %s" % (message, link)
                    #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                    discord_data = { "embeds": [{"title": "Tournament Winner", "description": d_message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)

                if group.slack_subscribe_tournaments and game.slack_webhook:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
                    s_message = "%s | %s" % (message, link)
                    slack_data = {'text': s_message}
                    data=json.dumps(slack_data)
                    resp, content = http_auth.request(group.slack_webhook,
                                      "POST",
                                      data,
                                      headers=headers)


        ## send everyone the new active list
        #taskUrl='/task/all/active/list'
        #taskqueue.add(url=taskUrl, queue_name='taskAllActiveList', countdown = 2,)

        taskUrl='/task/tournament/push'
        taskqueue.add(url=taskUrl, queue_name='tournamentPush', params={'key_id': tournament.key.id()}, countdown = 2,)

        ##  delete tournament chat
        taskUrl='/task/chat/channel/delete'
        taskqueue.add(url=taskUrl, queue_name='chatChannelDelete', params={'key_id': chat_channel.key.id()}, countdown = 4,)
