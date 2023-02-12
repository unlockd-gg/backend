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

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GameTransactionQueueProcessHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GameTransactionQueueProcessHandler")

        ## this is a game key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        lockController = TransactionLockController()
        transactionController = TransactionsController()
        gamesController = GamesController()

        ## has this queue run recently?
        ## pushable means that it hasn't run recently so go ahead with processing.

        pushable = lockController.pushable("game:%s"%key_id)

        ## we need the transactions in either case.
        pending_transactions = transactionController.get_pending_by_gameKeyId(int(key_id))

        if pushable:
            logging.info('PUSHABLE')
            ## process transactions

            game = gamesController.get_by_key_id(int(key_id))


            if not game:
                logging.error("game not found")
                return

            logging.info('Starting game.currencyBalance: %s' %game.currencyBalance)

            ## make sure the server does not go negative, after all are processed.
            results_positive = True
            amount_changed = 0

            ## loop through them

            # store the server's current balance
            if game.currencyBalance:
                tempCurrencyBalance = game.currencyBalance
            else:
                tempCurrencyBalance = 0

            for transaction in pending_transactions:
                logging.info("processing transaction in the amount of: %s" %transaction.amountInt)
                amount_changed = amount_changed + transaction.amountInt
                tempCurrencyBalance = tempCurrencyBalance + transaction.amountInt
                transaction.newBalanceInt = tempCurrencyBalance

            if game.currencyBalance:
                if game.currencyBalance + amount_changed < 0:
                    results_positive = False
            else:
                game.currencyBalance = 0

            if not results_positive:
                logging.error('NEGATIVE OCCURED')
                ## TODO deal with this.

            logging.info('Total amount_changed: %s' %amount_changed)


            ## apply the changes
            for transaction in pending_transactions:
                transaction.processed = True
                transactionController.update(transaction)


            logging.info('Game Balance was: %s' % game.currencyBalance )

            game.currencyBalance = game.currencyBalance + amount_changed

            logging.info('Game Balance changing to: %s' % game.currencyBalance)

            gamesController.update(game)

            ## update firebase
            taskUrl='/task/game/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game.key.id()}, countdown = 2,)

            ## do slack/discord pushes if enabled
            if game.slack_subscribe_transactions and game.slack_webhook:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "%s Transactions Processed: %s | Balance: %s" % (len(pending_transactions), amount_changed, game.currencyBalance)
                    slack_data = {'text': message}
                    data=json.dumps(slack_data)
                    resp, content = http_auth.request(game.slack_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('slack error')

            if game.discord_subscribe_transactions and game.discord_webhook_admin:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "%s Transactions Processed: %s | Balance: %s" % (len(pending_transactions), amount_changed, game.currencyBalance)
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Transactions Processed", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord error')


        else:
            logging.info('NOT PUSHABLE')
            ## are there pending transactions?
            if len(pending_transactions) > 0:
                logging.info('FOUND PENDING TRANSACTIONS')
                ## reschedule this task for later
                taskUrl='/task/game/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                        "key_id": key_id
                                                                                    }, countdown=2)
            else:
                logging.info('NO PENDING TRANSACTIONS')
                ## quit this task
                return
        return
