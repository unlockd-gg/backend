import logging
import datetime
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.handlers import BaseHandler
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.offers import OffersController
from apps.uetopia.controllers.vouchers import VouchersController
from apps.uetopia.controllers.badges import BadgesController

from configuration import *

class RemoveExpiredBadgesHandler(BaseHandler):
    def get(self):
        logging.info('Cron RemoveExpiredBadgesHandler')

        userController = UsersController()
        badgesController = BadgesController()
        offerController = OffersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()

        expired_badges = badgesController.get_expired()

        for expired_badge in expired_badges:
            logging.info('found expired badge')

            if expired_badge.autoRefresh:
                logging.info('auto-refresh is on.')

                # get the original offer
                offer = offerController.get_by_key_id(expired_badge.offerKeyId)

                if not offer:
                    logging.info('offer not found')
                    ## start a task to update the game player tags
                    taskUrl='/task/game/player/tags_update'
                    taskqueue.add(url=taskUrl, queue_name='gamePlayerUpdateTags', params={"key_id": expired_badge.gamePlayerKeyId}, countdown=2)

                    badgesController.delete(expired_badge)
                    continue

                # get the user
                user = userController.get_by_key_id(expired_badge.userKeyId)
                if not user:
                    logging.info('user not found')
                    ## start a task to update the game player tags
                    taskUrl='/task/game/player/tags_update'
                    taskqueue.add(url=taskUrl, queue_name='gamePlayerUpdateTags', params={"key_id": expired_badge.gamePlayerKeyId}, countdown=2)

                    badgesController.delete(expired_badge)
                    continue

                if user.currencyBalance < offer.price:
                    logging.info('user does not have enough balance')
                    ## start a task to update the game player tags
                    taskUrl='/task/game/player/tags_update'
                    taskqueue.add(url=taskUrl, queue_name='gamePlayerUpdateTags', params={"key_id": expired_badge.gamePlayerKeyId}, countdown=2)

                    badgesController.delete(expired_badge)
                    continue

                ## set up a new transaction
                ## calculate the uetopia rake
                uetopia_rake = int(offer.price * UETOPIA_GROSS_PERCENTAGE_RAKE)
                logging.info("uetopia_rake: %s" % uetopia_rake)

                remaining_to_game = offer.price - uetopia_rake
                logging.info("remaining_to_game: %s" % remaining_to_game)

                description = "Offer purchase - via badge renewal - from: %s" %user.title
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
                    transactionClass = "voucher_renewal",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_VOUCHER_REDEEM,
                    materialDisplayClass = "md-primary"
                )

                ## Transaction for uetopia rake - this is marked as processed - just recording it.
                ## only do this if the value is more than zero
                recipient_transaction_key_id = None
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
                        transactionClass = "game voucher renewal rake",
                        transactionSender = False,
                        transactionRecipient = True,
                        submitted = True,
                        processed = True,
                        materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                        materialDisplayClass = "md-primary"
                    )
                    recipient_transaction_key_id = recipient_transaction.key.id()

                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                pushable = lockController.pushable("game:%s"%offer.gameKeyId)
                if pushable:
                    logging.info('game pushable')
                    taskUrl='/task/game/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                            "key_id": offer.gameKeyId
                                                                                        }, countdown=2)

                ## create the transaction for the user even if zero
                description = "Renewed voucher: %s" %offer.title
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

                end_date = datetime.datetime.now() + datetime.timedelta(days=offer.duration_days, seconds=offer.duration_seconds)
                expired_badge.ends = end_date
                badgesController.update(expired_badge)

                ## push an alert out to firebase
                description = "%s : badge auto-renewed : %s" %(offer.gameTitle, offer.title)
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

            else:
                logging.info('not autoRefresh')

                ## start a task to update the game player tags
                taskUrl='/task/game/player/tags_update'
                taskqueue.add(url=taskUrl, queue_name='gamePlayerUpdateTags', params={"key_id": expired_badge.gamePlayerKeyId}, countdown=2)

                badgesController.delete(expired_badge)
                continue

        badgecount = len(expired_badges)

        return self.render_json_response(
            badgecount= badgecount
        )
