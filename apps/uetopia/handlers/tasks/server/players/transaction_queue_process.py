import endpoints
import logging
import uuid
import urllib
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

from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ServerPlayerTransactionQueueProcessHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ServerPlayerTransactionQueueProcessHandler")

        ## this is a serverPlayer key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        lockController = TransactionLockController()
        transactionController = TransactionsController()

        ## has this queue run recently?
        ## pushable means that it hasn't run recently so go ahead with processing.

        pushable = lockController.pushable("serverplayer:%s"%key_id)

        ## we need the transactions in either case.
        pending_transactions = transactionController.get_pending_by_serverPlayerKeyId(int(key_id))

        if pushable:
            logging.info('PUSHABLE')
            ## process transactions

            spController = ServerPlayersController()

            server_player = spController.get_by_key_id(int(key_id))
            logging.info('server_player Balance detected: %s' % server_player.currencyCurrent )

            if not server_player:
                logging.error('server_player not found')
                return

            ## make sure the server_player does not go negative, after all are processed.
            results_positive = True
            amount_changed = 0

            ## loop through them

            # store the server_player's current elsewhere for a sec
            tempCurrencyBalance = server_player.currencyCurrent
            for transaction in pending_transactions:
                logging.info("processing transaction in the amount of: %s" %transaction.amountInt)
                amount_changed = amount_changed + transaction.amountInt
                tempCurrencyBalance = tempCurrencyBalance + transaction.amountInt
                transaction.newBalanceInt = tempCurrencyBalance

            if server_player.currencyCurrent + amount_changed < 0:
                results_positive = False

            if not results_positive:
                logging.error('NEGATIVE OCCURED')
                ## TODO deal with this.

            ## apply the changes
            for transaction in pending_transactions:
                transaction.processed = True
                transactionController.update(transaction)

            logging.info('server_player Balance was: %s' % server_player.currencyCurrent )

            server_player.currencyCurrent = server_player.currencyCurrent + amount_changed

            logging.info('server_player Balance changing to: %s' % server_player.currencyCurrent )
            spController.update(server_player)

            ## update firebase

            #taskUrl='/task/user/firebase/update'
            #taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id()}, countdown = 2,)

        else:
            logging.info('NOT PUSHABLE')
            ## are there pending transactions?
            if len(pending_transactions) > 0:
                logging.info('FOUND PENDING TRANSACTIONS')
                ## reschedule this task for later
                taskUrl='/task/server/player/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='serverPlayerTransactionProcess', params={
                                                                                        "key_id": key_id
                                                                                    }, countdown=2)
            else:
                logging.info('NO PENDING TRANSACTIONS')
                ## quit this task
                return
        return
