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

from configuration import *

class TaskTournamentFinishSignups(BaseHandler):
    """
    Move a tournament from signup mode into play started mode if possible

    """
    def post(self):
        """

        """

        logging.info('TaskTournamentFinishSignups')

        userController = UsersController()
        mpController = MatchPlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        tournamentController = TournamentsController()
        teamController = TeamsController()
        teamMembersController = TeamMembersController()
        gameModeController = GameModesController()

        key_id = self.request.get('key_id')

        tournament = tournamentController.get_by_key_id(int(key_id))

        ## get chat channel for this tournament
        chat_channel = ChatChannelsController().get_by_channel_type_refKeyId("tournament", tournament.key.id())
        if not chat_channel:
            logging.error('chat channel not found for tournament')
            return

        ## this used to be:
        #teams = teamController.get_list_by_tournament_full(int(key_id))

        ## but this does not make sense for games that allow multiple game mode tournaments.
        ## for example if we allow 1v1 and 2v2 tournaments, the 1v1 tournament team can never be full.
        ## changing this
        teams = teamController.get_list_by_tournament(int(key_id))

        logging.info('len(teams): %s'% len(teams) )

        team_count_within_bounds = False
        team_count_max = False
        ## make sure there are enough teams joined
        if len(teams) >= tournament.teamMin:
            logging.info("minimum team requirement met")
            if len(teams) >= tournament.teamMax:
                logging.info("maximum team requirement met")
                team_count_max = True
                team_count_within_bounds = True


        if tournament.signupEndTime > datetime.datetime.now():
            logging.info('Signups are open.')
            if not team_count_max:
                ## push the tournament and exit if we're not full
                taskUrl='/task/tournament/push'
                taskqueue.add(url=taskUrl, queue_name='tournamentPush', params={'key_id': tournament.key.id()}, countdown = 2,)
                return
        else:
            logging.info('Signups are closed.')
            if not team_count_within_bounds:
                logging.info('Team count not within bounds.')
                ## TODO Purge and give back host deposit.
                ## this will get cought in the cron job too, just takes longer.
                return

        ## TODO prevent multiple starts
        ## we're protected by a memcache check, but we should examine bools here.

        ## At this point, we have a tournament that should start.
        ## it either has reached teamMax
        ## or it has at least teamMin and the timer has run out.

        ## get the game mode we're using
        game_mode = gameModeController.get_by_key_id(tournament.gameModeKeyId)
        if not game_mode:
            logging.error("game mode not found")
            return

        #estimated_winnings = 0
        total_players = 0
        total_buyin_amount = 0

        ## go through the teams, and get all of the players for buy-in processing
        for team in teams:
            team_players = teamMembersController.get_by_teamKeyId(team.key.id())
            ## TODO sanity check the team
            for team_player in team_players:
                ## get the user record
                t_player_user = userController.get_by_key_id(team_player.userKeyId)
                ## make sure each player has the balance to cover it - maybe they did something before play start?
                logging.info("team_player.userKeyId: %s"%team_player.userKeyId)
                logging.info("t_player_user.currencyBalance: %s"%t_player_user.currencyBalance)


                if not t_player_user.currencyBalance >= tournament.playerBuyIn:
                    logging.error("player does not have enough funds to cover the buyin")
                    ## TODO deal with this case
                    return
                total_players = total_players +1
                total_buyin_amount = total_buyin_amount + tournament.playerBuyIn

                ## Set up transactions for the user and push

                description = "Paid Tournament Buy-In: %s for %s" %(tournament.title, tournament.playerBuyIn)
                transactionController.create(
                    amountInt = -tournament.playerBuyIn,
                    description = description,
                    userKeyId = t_player_user.key.id(),
                    firebaseUser = t_player_user.firebaseUser,
                    transactionType = "user",
                    transactionClass = "tournament_buyin",
                    transactionSender = True,
                    transactionRecipient = False,
                    #recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_TOURNAMENT,
                    materialDisplayClass = "md-accent"
                )
                pushable = lockController.pushable("user:%s"%t_player_user.key.id())
                if pushable:
                    logging.info('user pushable')
                    taskUrl='/task/user/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": t_player_user.key.id()
                                                                                    }, countdown=2)



                # Also set up a transaction for the tournament
                ## we're setting them as processed because we don't need to worry about the 1 second rule in this case.
                ## these are mostly here so we can keep track of everything and potentially do refunds.

                description = "Tournament Buy-In: %s for %s" %(tournament.title, tournament.playerBuyIn)
                transactionController.create(
                    amountInt = tournament.playerBuyIn,
                    description = description,
                    userKeyId = t_player_user.key.id(),
                    firebaseUser = t_player_user.firebaseUser,
                    transactionType = "tournament",
                    transactionClass = "tournament_buyin",
                    transactionSender = False,
                    transactionRecipient = True,
                    #recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = True,
                    materialIcon = MATERIAL_ICON_TOURNAMENT,
                    materialDisplayClass = "md-primary"
                )


                tournament.currencyBalance = tournament.currencyBalance + tournament.playerBuyIn

            ## change the state of all of the teams
            team.activeInTournament = True
            teamController.update(team)

        ## calculate the play tiers
        ## TODO allow for different tournament types
        ## for now it's just single elimination

        ## determine if we have even teams
        remainder = len(teams) %2
        ## the remainder are "byes" which go to round 2 automatically.

        ## Total number of matches
        ## TODO if we want to calculate 2nd and 3rd place we need one more match
        match_count = len(teams) -1

        ## deduct server fees

        tournament.server_fees = (game_mode.admissionFeePerPlayer - (game_mode.winRewardPerPlayer / 2)) * match_count
        logging.info("tournament.server_fees : %s "%tournament.server_fees  )

        tournament.estimatedTotalWinnings = tournament.currencyBalance - tournament.server_fees
        logging.info("tournament.estimatedTotalWinnings: %s "%tournament.estimatedTotalWinnings )

        ## determine number of rounds
        rounds = 1
        rounds_multiplier = 2
        while (rounds_multiplier < len(teams)):
            logging.info("rounds_multiplier: %s "%rounds_multiplier )
            rounds = rounds +1
            rounds_multiplier = rounds_multiplier*2

        logging.info("remainder: %s" %remainder)
        logging.info("match_count: %s" %match_count)
        logging.info("rounds: %s" %rounds)

        ## change the state of the tournament
        #estimated_winnings = estimated_winnings + tournament.additionalPrizeFromHost

        tournament.signupsFinished = True
        #tournament.estimatedTotalWinnings = estimated_winnings
        tournament.total_rounds = rounds
        tournament.current_round = 0
        tournament.total_buyin_amount = total_buyin_amount
        tournament.total_players = total_players

        tournamentController.update(tournament)

        ## alerts and pushes

        ## kick off a new task to start the first round
        ## TODO calculate the countdown based on the play start timer
        taskUrl='/task/tournament/round/start'
        taskqueue.add(url=taskUrl, queue_name='tournamentProcessing', params={'key_id': tournament.key.id()}, countdown = 2,)
