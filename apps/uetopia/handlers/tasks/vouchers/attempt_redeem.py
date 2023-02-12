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
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.vendors import VendorsController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.vouchers import VouchersController
from apps.uetopia.controllers.voucher_claims import VoucherClaimsController
from apps.uetopia.controllers.offers import OffersController
from apps.uetopia.controllers.badges import BadgesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class VoucherAttemptRedeemHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] VoucherAttemptRedeemHandler")

        ## this is a voucher key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        userController = UsersController()
        gamePlayerController = GamePlayersController()
        lockController = TransactionLockController()
        transactionController = TransactionsController()
        offerController = OffersController()
        voucherController = VouchersController()
        voucherClaimController = VoucherClaimsController()
        badgeController = BadgesController()

        voucher = voucherController.get_by_key_id(int(key_id))
        if not voucher:
            logging.info('voucher not found')
            return

        offer = offerController.get_by_key_id(voucher.offerKeyId)
        if not offer:
            logging.info('offer not found')
            return

        voucher_claims_sorted = voucherClaimController.get_all_sorted_by_voucherKeyId(voucher.key.id())

        ## the first claim in this list is valid.
        ## redeem it, then delete everything.
        ## optionally delete the voucher as well if it was single use.

        if len(voucher_claims_sorted) > 0:
            logging.info('found at least one claim')

            #Loop over them, accepting the first valid. and reject everything else
            for voucher_claim in voucher_claims_sorted:
                logging.info('checking claim')

                user = userController.get_by_key_id(voucher_claim.userKeyId)
                if not user:
                    logging.info('user not found')
                    continue

                ## make sure the user has enough balance
                if user.currencyBalance < offer.price:
                    logging.info('user does not have enough balance')
                    continue

                game_player = gamePlayerController.get_by_gameKeyId_userKeyId(voucher.gameKeyId, user.key.id())

                if not game_player:
                    logging.info('game player not found.  This should not happen here.')
                    continue

                ## any other checks?

                ## redeem the claim



                ## only create a transaction for the game if non-zero
                recipient_transaction_key_id = None
                if offer.price > 0:
                    logging.info('price is greater than zero - setting up transaction for the game')

                    ## calculate the uetopia rake
                    uetopia_rake = int(offer.price * UETOPIA_GROSS_PERCENTAGE_RAKE)
                    logging.info("uetopia_rake: %s" % uetopia_rake)

                    remaining_to_game = offer.price - uetopia_rake
                    logging.info("remaining_to_game: %s" % remaining_to_game)

                    description = "Offer purchase from: %s" %user.title
                    recipient_transaction = transactionController.create(
                        amountInt = remaining_to_game,
                        amountIntGross = offer.price,
                        ##amount = ndb.FloatProperty(indexed=False) # for display
                        ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                        ##newBalance = ndb.FloatProperty(indexed=False) # for display
                        description = offer.description,
                        ##userKeyId = user.key.id(),
                        ##firebaseUser = user.firebaseUser,
                        ##targetUserKeyId = ndb.IntegerProperty()
                        gameKeyId = offer.gameKeyId,
                        gameTitle = offer.gameTitle,

                        ##  transactions are batched and processed all at once.
                        transactionType = "game",
                        transactionClass = "voucher_redeem",
                        transactionSender = False,
                        transactionRecipient = True,
                        submitted = True,
                        processed = False,
                        materialIcon = MATERIAL_ICON_VOUCHER_REDEEM,
                        materialDisplayClass = "md-primary"
                    )

                    ## Transaction for uetopia rake - this is marked as processed - just recording it.
                    ## only do this if the value is more than zero
                    if uetopia_rake > 0:
                        description = "Game Donation Percentage from: %s" %user.title
                        recipient_transaction = transactionController.create(
                            amountInt = uetopia_rake,
                            description = description,
                            #serverKeyId = server.key.id(),
                            #serverTitle = server.title,
                            gameKeyId = offer.gameKeyId,
                            gameTitle = offer.gameTitle,
                            transactionType = "uetopia",
                            transactionClass = "game voucher redeem rake",
                            transactionSender = False,
                            transactionRecipient = True,
                            submitted = True,
                            processed = True,
                            materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                            materialDisplayClass = "md-primary"
                        )

                    ## only start pushable tasks.  If they are not pushable, there is already a task running.
                    pushable = lockController.pushable("game:%s"%offer.gameKeyId)
                    if pushable:
                        logging.info('game pushable')
                        taskUrl='/task/game/transaction/process'
                        taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                                "key_id": offer.gameKeyId
                                                                                            }, countdown=2)

                ## create the transaction for the user even if zero
                description = "Redeemed voucher: %s" %voucher.title
                transactionController.create(
                    amountInt = -offer.price,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = offer.description,
                    userKeyId = user.key.id(),
                    firebaseUser = user.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    ##serverKeyId = server.key.id(),
                    ##serverTitle = server.title()
                    ##  transactions are batched and processed all at once.
                    transactionType = "user",
                    transactionClass = "voucher_redeem",
                    transactionSender = True,
                    transactionRecipient = False,
                    recipientTransactionKeyId = recipient_transaction_key_id,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_VOUCHER_REDEEM,
                    materialDisplayClass = "md-accent"
                )
                pushable = lockController.pushable("user:%s"%user.key.id())
                if pushable:
                    logging.info('user pushable')
                    taskUrl='/task/user/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": user.key.id()
                                                                                    }, countdown=2)

                ## create the badge
                # calculate end date
                end_date = None
                autoRefresh = False
                if offer.timed:
                    end_date = datetime.datetime.now() + datetime.timedelta(days=offer.duration_days, seconds=offer.duration_seconds)

                    if offer.autoRefreshCapable and voucher_claim.autoRefresh:
                        autoRefresh = True

                badge = badgeController.create(
                    ends = end_date,
                    title = offer.title,
                    description = offer.description,
                    gameKeyId = offer.gameKeyId,
                    gameTitle = offer.gameTitle,
                    offerKeyId = offer.key.id(),
                    offerTitle = offer.title,
                    voucherKeyId = voucher.key.id(),
                    voucherTitle = voucher.title,
                    userKeyId = user.key.id(),
                    userTitle = user.title,
                    gamePlayerKeyId = game_player.key.id(),
                    #gamePlayerTitle = game_player.title,
                    offerType = offer.offerType,
                    tags = offer.tags,
                    icon_url = offer.icon_url,
                    active = True,
                    autoRefresh = autoRefresh
                )

                ## start a task to update the game player tags
                taskUrl='/task/game/player/tags_update'
                taskqueue.add(url=taskUrl, queue_name='gamePlayerUpdateTags', params={
                                                                                        "key_id": game_player.key.id()
                                                                                    }, countdown=2)

                ## push an alert out to firebase
                description = "%s : badge granted : %s" %(offer.gameTitle, offer.title)
                game_sref='#/games/%s' %offer.gameKeyId
                taskUrl='/task/user/alert/create'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': user.firebaseUser,
                                                                                'material_icon': MATERIAL_ICON_VOUCHER_REDEEM,
                                                                                'importance': 'md-primary',
                                                                                ## TODO this message can be more helpful
                                                                                'message_text': description,
                                                                                'action_button_color': 'primary',
                                                                                'action_button_sref': game_sref
                                                                                }, countdown = 1,)

                ## everything is done
                ## delete the voucher and all voucher claims
                break

            for voucher_claim in voucher_claims_sorted:
                logging.info('deleting claim')
                voucherClaimController.delete(voucher_claim)

            logging.info('deleting voucher')
            voucherController.delete(voucher)

            return



        else:
            logging.info('no claims to this voucher were found - aborting')
            return
