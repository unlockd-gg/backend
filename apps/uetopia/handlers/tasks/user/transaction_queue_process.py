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

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class UserTransactionQueueProcessHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] UserTransactionQueueProcessHandler")

        ## this is a server key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        lockController = TransactionLockController()
        transactionController = TransactionsController()

        ## has this queue run recently?
        ## pushable means that it hasn't run recently so go ahead with processing.

        pushable = lockController.pushable("user:%s"%key_id)

        ## we need the transactions in either case.
        pending_transactions = transactionController.get_pending_by_userKeyId(int(key_id))

        if pushable:
            logging.info('PUSHABLE')
            ## process transactions

            usersController = UsersController()

            user = usersController.get_by_key_id(int(key_id))
            logging.info('User Balance detected: %s' % user.currencyBalance )

            if not user:
                logging.error('User not found')
                return

            ## make sure the server does not go negative, after all are processed.
            results_positive = True
            amount_changed = 0

            ## loop through them

            # store the user's current elsewhere for a sec
            tempCurrencyBalance = user.currencyBalance
            for transaction in pending_transactions:
                logging.info("processing transaction in the amount of: %s" %transaction.amountInt)
                amount_changed = amount_changed + transaction.amountInt
                tempCurrencyBalance = tempCurrencyBalance + transaction.amountInt
                transaction.newBalanceInt = tempCurrencyBalance

            if user.currencyBalance + amount_changed < 0:
                results_positive = False

            if not results_positive:
                logging.error('NEGATIVE OCCURED')
                ## TODO deal with this.

            ## apply the changes
            for transaction in pending_transactions:
                transaction.processed = True
                transactionController.update(transaction)

            logging.info('User Balance was: %s' % user.currencyBalance )

            user.currencyBalance = user.currencyBalance + amount_changed

            logging.info('User Balance changing to: %s' % user.currencyBalance )
            usersController.update(user)

            ## update firebase

            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(), 'skip_friends': True}, countdown = 2,)

        else:
            logging.info('NOT PUSHABLE')
            ## are there pending transactions?
            if len(pending_transactions) > 0:
                logging.info('FOUND PENDING TRANSACTIONS')
                ## reschedule this task for later
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": key_id
                                                                                    }, countdown=2)
            else:
                logging.info('NO PENDING TRANSACTIONS')
                ## quit this task
                return
        return
