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

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GroupTransactionQueueProcessHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GroupTransactionQueueProcessHandler")

        ## this is a group key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        lockController = TransactionLockController()
        transactionController = TransactionsController()
        groupsController = GroupsController()

        ## has this queue run recently?
        ## pushable means that it hasn't run recently so go ahead with processing.

        pushable = lockController.pushable("group:%s"%key_id)

        ## we need the transactions in either case.
        pending_transactions = transactionController.get_pending_by_groupKeyId(int(key_id))

        if pushable:
            logging.info('PUSHABLE')
            ## process transactions

            group = groupsController.get_by_key_id(int(key_id))


            if not group:
                logging.error("group not found")
                return

            logging.info('Starting group.currencyBalance: %s' %group.currencyBalance)

            ## make sure the group does not go negative, after all are processed.
            results_positive = True
            amount_changed = 0

            ## loop through them

            # store the group's current balance
            if group.currencyBalance:
                tempCurrencyBalance = group.currencyBalance
            else:
                tempCurrencyBalance = 0

            for transaction in pending_transactions:
                logging.info("processing transaction in the amount of: %s" %transaction.amountInt)
                amount_changed = amount_changed + transaction.amountInt
                tempCurrencyBalance = tempCurrencyBalance + transaction.amountInt
                transaction.newBalanceInt = tempCurrencyBalance

            if group.currencyBalance:
                if group.currencyBalance + amount_changed < 0:
                    results_positive = False
            else:
                group.currencyBalance = 0

            if not results_positive:
                logging.error('NEGATIVE OCCURED')
                ## TODO deal with this.

            logging.info('Total amount_changed: %s' %amount_changed)


            ## apply the changes
            for transaction in pending_transactions:
                transaction.processed = True
                transactionController.update(transaction)


            logging.info('Group Balance was: %s' % group.currencyBalance )

            group.currencyBalance = group.currencyBalance + amount_changed

            logging.info('Group Balance changing to: %s' % group.currencyBalance)

            groupsController.update(group)

            ## update firebase
            taskUrl='/task/group/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': group.key.id()}, countdown = 2,)

            ## do slack/discord pushes if enabled
            if group.slack_subscribe_transactions and group.slack_webhook:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "%s Transactions Processed: %s | Balance: %s" % (len(pending_transactions), amount_changed, group.currencyBalance)
                    slack_data = {'text': message}
                    data=json.dumps(slack_data)
                    resp, content = http_auth.request(group.slack_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('slack error')

            if group.discord_subscribe_transactions and group.discord_webhook:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "%s Transactions Processed: %s | Balance: %s" % (len(pending_transactions), amount_changed, group.currencyBalance)
                    url = "http://ue4topia.appspot.com/#/developer/group/%s" % group.key.id()
                    discord_data = { "embeds": [{"title": "Transactions Processed", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group.discord_webhook_admin,
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
                taskUrl='/task/group/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                        "key_id": key_id
                                                                                    }, countdown=2)
            else:
                logging.info('NO PENDING TRANSACTIONS')
                ## quit this task
                return
        return
