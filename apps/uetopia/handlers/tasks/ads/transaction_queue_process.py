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
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.ads import AdsController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class AdTransactionQueueProcessHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GroupTransactionQueueProcessHandler")

        ## this is a group key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        lockController = TransactionLockController()
        transactionController = TransactionsController()
        groupsController = GroupsController()
        groupGamesController = GroupGamesController()
        adController = AdsController()
        gController = GamesController()

        ## has this queue run recently?
        ## pushable means that it hasn't run recently so go ahead with processing.

        pushable = lockController.pushable("ad:%s"%key_id)

        ## we need the transactions in either case.
        pending_transactions = transactionController.get_pending_by_adKeyId(int(key_id))

        if pushable:
            logging.info('PUSHABLE')
            ## process transactions

            ad = adController.get_by_key_id(int(key_id))


            if not ad:
                logging.error("ad not found")
                return

            logging.info('Starting ad.currencyBalance: %s' %ad.currencyBalance)

            ## make sure the ad does not go negative, after all are processed.
            results_positive = True
            amount_changed = 0

            ## loop through them

            # store the group's current balance
            if ad.currencyBalance:
                tempCurrencyBalance = ad.currencyBalance
            else:
                tempCurrencyBalance = 0

            ## First just add up all of the transactions.
            ## Ad impressions will be coming through as negative numbers becuase they are withdrawals

            count_shown = 0


            for transaction in pending_transactions:
                logging.info("processing transaction in the amount of: %s" %transaction.amountInt)
                amount_changed = amount_changed + transaction.amountInt
                tempCurrencyBalance = tempCurrencyBalance + transaction.amountInt
                transaction.newBalanceInt = tempCurrencyBalance
                gameTitle = transaction.gameTitle
                count_shown = count_shown + 1

            ## calculate the uetopia rake
            uetopia_rake = int(amount_changed * UETOPIA_GROSS_PERCENTAGE_RAKE)
            logging.info("uetopia_rake: %s" % uetopia_rake)

            remaining_revenue_to_game = amount_changed - uetopia_rake
            logging.info("remaining_revenue_to_game: %s" % remaining_revenue_to_game)

            ## remaining revenue is still negative here.
            if remaining_revenue_to_game < 0:
                logging.info('found revenue that needs to be sent to the game.')

                ## Create a transaction for the game
                description = "Ad revenue from: %s" % ad.title
                recipient_transaction = transactionController.create(
                    amountInt = -remaining_revenue_to_game,  #flip to positive
                    amountIntGross = -amount_changed,  #flip to positive
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    ##userKeyId = authorized_user.key.id(),
                    ##firebaseUser = authorized_user.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    gameKeyId = ad.gameKeyId,
                    gameTitle = ad.gameTitle,

                    ##  transactions are batched and processed all at once.
                    transactionType = "game",
                    transactionClass = "ad_revenue",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_AD_SHOWN,
                    materialDisplayClass = "md-primary"
                )

                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                pushable = lockController.pushable("game:%s"%ad.gameKeyId)
                if pushable:
                    logging.info('game pushable')
                    taskUrl='/task/game/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                            "key_id": ad.gameKeyId
                                                                                        }, countdown=2)



            if ad.currencyBalance:
                if ad.currencyBalance + amount_changed < 0:
                    results_positive = False
            else:
                ad.currencyBalance = 0

            if not results_positive:
                logging.error('NEGATIVE OCCURED')
                ## TODO deal with this.

            logging.info('Total amount_changed: %s' %amount_changed)


            ## apply the changes
            for transaction in pending_transactions:
                transaction.processed = True
                transactionController.update(transaction)


            logging.info('ad Balance was: %s' % ad.currencyBalance )
            logging.info('ad Count was: %s' % ad.count_shown )

            ad.currencyBalance = ad.currencyBalance + amount_changed
            ad.count_shown = ad.count_shown + count_shown

            logging.info('ad Balance changing to: %s' % ad.currencyBalance)
            logging.info('ad Count changing to: %s' % ad.count_shown)

            ## get the group game for discord info
            group_game = groupGamesController.get_by_groupKeyId_gameKeyId(ad.groupKeyId, ad.gameKeyId)
            game = gController.get_by_key_id(ad.gameKeyId)

            ## check to see if the ad should be closed out
            if ad.count_shown >= ad.number_of_impressions:
                logging.info('count shown >= number of impressions - closing out this ad')

                ad.active = False
                ad.finalized = True

                ## set up the remaining refund back to the group

                unspent_balance = ad.currencyBalance

                ad.currencyBalance = 0


                ## make a new transaction and mark it as processed
                ## one for the AD
                description = "Unspent balance refunded back to group"
                transactionController.create(
                    amountInt = -unspent_balance,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    newBalanceInt = 0,
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    #userKeyId = authorized_user.key.id(),
                    #firebaseUser = authorized_user.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    adKeyId = ad.key.id(),
                    adTitle = ad.title,
                    ##  transactions are batched and processed all at once.
                    transactionType = "ad",
                    transactionClass = "unspent_refund",
                    transactionSender = True,
                    transactionRecipient = False,
                    #recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = True,
                    materialIcon = MATERIAL_ICON_AD_REFUND,
                    materialDisplayClass = "md-accent"
                )

                ## one for the group
                description = "Ad finalize unspent: %s" %ad.title
                transactionController.create(
                    amountInt = unspent_balance,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    #userKeyId = authorized_user.key.id(),
                    #firebaseUser = authorized_user.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    groupKeyId = ad.groupKeyId,
                    groupTitle = ad.groupTitle,
                    ##  transactions are batched and processed all at once.
                    transactionType = "group",
                    transactionClass = "ad_unspent_refund",
                    transactionSender = False,
                    transactionRecipient = True,
                    #recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_AD_REFUND,
                    materialDisplayClass = "md-primary"
                )

                ## only start transaction push for the group here
                pushable = lockController.pushable("group:%s"% ad.groupKeyId)
                if pushable:
                    logging.info('group pushable')
                    taskUrl='/task/group/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                        "key_id": ad.groupKeyId
                                                                                    }, countdown=2)


                ad.refunded = True

                ## discord push to group/ad
                if group_game:
                    if group_game.discord_subscribe_game_ad_status_changes:

                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        link = "https://ue4topia.appspot.com/#/groups/%s/games/%s/ad/%s" % (ad.groupKeyId, ad.groupGameKeyId, ad.key.id())
                        message = "Ad finalized:  %s" % (link)
                        discord_data = { "embeds": [{"title": "Ad finalized", "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(group_game.discordWebhook,
                                          "POST",
                                          data,
                                          headers=headers)


                ## discord push to game
                if game:
                    if game.discord_webhook_admin:
                        message = "Ad finalized"
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        link = "https://ue4topia.appspot.com/#/games/%s" % (game.key.id())
                        discord_data = { "embeds": [{"title": "Ad finalized", "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)

                adController.update(ad)

                return

            ## the ad did not need to be closed out

            ## push a discord alert out to the group/ad
            if group_game:
                if group_game.discord_subscribe_game_ad_status_changes:

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/groups/%s/games/%s/ad/%s" % (ad.groupKeyId, ad.groupGameKeyId, ad.key.id())
                    message = "Ad impressions shown:  %s %s" % (count_shown, link)
                    discord_data = { "embeds": [{"title": "Ad impressions shown", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group_game.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)

            ## push a discord alert out to the game?

            adController.update(ad)



        else:
            logging.info('NOT PUSHABLE')
            ## are there pending transactions?
            if len(pending_transactions) > 0:
                logging.info('FOUND PENDING TRANSACTIONS')
                ## reschedule this task for later
                taskUrl='/task/ad/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='adTransactionProcess', params={
                                                                                        "key_id": key_id
                                                                                    }, countdown=2)
            else:
                logging.info('NO PENDING TRANSACTIONS')
                ## quit this task
                return
        return
