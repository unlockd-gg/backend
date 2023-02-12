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

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ServerTransactionQueueProcessHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ServerTransactionQueueProcessHandler")

        ## this is a server key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        lockController = TransactionLockController()
        transactionController = TransactionsController()
        serversController = ServersController()

        ## has this queue run recently?
        ## pushable means that it hasn't run recently so go ahead with processing.

        pushable = lockController.pushable("server:%s"%key_id)

        ## we need the transactions in either case.
        pending_transactions = transactionController.get_pending_by_serverKeyId(int(key_id))

        if pushable:
            logging.info('PUSHABLE')
            ## process transactions

            server = serversController.get_by_key_id(int(key_id))


            if not server:
                logging.error("server not found")
                return

            logging.info('Starting server.serverCurrency: %s' %server.serverCurrency)

            ## make sure the server does not go negative, after all are processed.
            results_positive = True
            amount_changed = 0

            ## loop through them

            # store the server's current balance
            if server.serverCurrency:
                tempCurrencyBalance = server.serverCurrency
            else:
                server.serverCurrency = 0
                tempCurrencyBalance = 0

            for transaction in pending_transactions:
                logging.info("processing transaction in the amount of: %s" %transaction.amountInt)
                amount_changed = amount_changed + transaction.amountInt
                tempCurrencyBalance = tempCurrencyBalance + transaction.amountInt
                transaction.newBalanceInt = tempCurrencyBalance

            if server.serverCurrency:
                if server.serverCurrency + amount_changed < 0:
                    results_positive = False
            else:
                server.serverCurrency = 0

            if not results_positive:
                logging.error('NEGATIVE OCCURED')
                ## TODO deal with this.

            logging.info('Total amount_changed: %s' %amount_changed)


            ## apply the changes
            for transaction in pending_transactions:
                transaction.processed = True
                transactionController.update(transaction)


            logging.info('Server Balance was: %s' % server.serverCurrency )

            server.serverCurrency = server.serverCurrency + amount_changed

            logging.info('Server Balance changing to: %s' % server.serverCurrency )

            if server.serverCurrency > server.server_to_game_transfer_threshold:
                logging.info('server_to_game_transfer_threshold exceeded.')
                server.server_to_game_transfer_exceeded = True

            serversController.update(server)

            ## update firebase
            if not server.invisible:
                logging.info('visible')
                if not server.invisible_developer_setting:
                    logging.info('visible-dev')
                    taskUrl='/task/server/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server.key.id()}, countdown = 2,)


        else:
            logging.info('NOT PUSHABLE')
            ## are there pending transactions?
            if len(pending_transactions) > 0:
                logging.info('FOUND PENDING TRANSACTIONS')
                ## reschedule this task for later
                taskUrl='/task/server/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='serverTransactionProcess', params={
                                                                                        "key_id": key_id
                                                                                    }, countdown=2)
            else:
                logging.info('NO PENDING TRANSACTIONS')
                ## quit this task
                return
        return
