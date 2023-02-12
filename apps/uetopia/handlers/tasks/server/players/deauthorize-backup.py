import logging
import re
import os
import datetime
import json
import uuid
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController

from apps.uetopia.controllers.match_results import MatchResultsController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.utilities.server_player_deactivate import deactivate_player

#from apps.uetopia.controllers.sense import SenseController

#from apps.uetopia.utilities.player.experience import process_player_experience

from configuration import *

class TaskServerDeauthorize(BaseHandler):
    """
    Deauthorize a player

    """
    def post(self):
        """

        """
        server_player_member_key_id = int(self.request.get('key_id'))

        spmController = ServerPlayersController()
        ucontroller = UsersController()
        server_controller = ServersController()

        server_player = spmController.get_by_key_id(server_player_member_key_id)

        user = ucontroller.get_by_key_id(server_player.userKeyId)
        server = server_controller.get_by_key_id(server_player.serverKeyId)

        # TODO might want to handle this case a bit better.
        # A user could end up deauthorizing while still active in game.

        #if server_player_member.active:
        #    return False

        if not server_player.authorized:
            return

        if server_player.banned:
            return

        logging.info("performing pending deauth")

        ## Calculate the btc_hold difference
        currency_hold_difference = server_player.currencyStart - server_player.currencyCurrent
        logging.info("currency_hold_difference: %s" %currency_hold_difference)

        ## update the player's btc balance
        ## this happens in transaction processing, not here.
        ##user.currencyBalance = user.currencyBalance + server_player.currencyCurrent

        # For sense
        sense_amount = server_player.currencyCurrent

        ###  BALANCE SHOULD NOT CHANGE HERE!

        #player.bitcoinBalanceSatoshi = player.bitcoinBalanceSatoshi + server_player_member.btcHoldCurrent
        #player.bitcoinBalance = float(player.bitcoinBalanceSatoshi) / 100000000.

        description = "Left: %s" %server.title

        ## Create a transaction for the deposit
        transaction = TransactionsController().create(
            userKeyId = user.key.id(),
            firebaseUser = user.firebaseUser,
            description = description,
            ##confirmations = 0,
            amountInt = server_player.currencyCurrent,
            #serverKeyId = server.key.id(),
            #serverTitle = server.title,
            ##amount = currency_hold / 100000000. * -1,
            #newBalanceInt = authorized_user.currencyBalance,
            #newBalance = float(authorized_user.currencyBalance) / 100000000.
            transactionType = "user",
            transactionClass = "server deactivate",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            )

        ## Check to see if the user is a referral, which still needs to be credited to the player who referred them.
        """
        if player.referral_initiated:
            logging.info("player.referral_initiated")
            if not player.referral_paid:
                logging.info("referral not paid")

                ## Make sure that played is set to true.
                player.referral_played = True


        if server_player_member.experience:
            if not player.experience:
                player.experience = 0
            player = process_player_experience(player, server_player_member.experience)

        ## TODO deal with playstyle
        """


        #ucontroller.update(user)

        server_player.pending_deauthorize = False
        server_player.pending_authorize = False
        server_player.currencyEnd = server_player.currencyCurrent
        server_player.active = False
        server_player.authorized = False
        server_player.deAuthCount = server_player.deAuthCount + 1
        server_player.currentCurrent = 0
        server_player.experience = 0

        spmController.update(server_player)

        # check to see if the updates can be pushed:

        lockController = TransactionLockController()

        ##  update firebase server player record
        taskUrl='/task/server/player/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id()}, countdown = 2,)

        pushable = lockController.pushable("user:%s"%user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": user.key.id()
                                                                            }, countdown=2)
