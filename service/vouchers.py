import endpoints
import logging
import uuid
import urllib
import json
import dateutil.parser
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

##from apps.uetopia.providers import firebase_helper

## endpoints v2 wants a "collection" so it can build the openapi files
#from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.models.vouchers import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController

from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.offers import OffersController
from apps.uetopia.controllers.vouchers import VouchersController
from apps.uetopia.controllers.voucher_claims import VoucherClaimsController
from apps.uetopia.controllers.offers import OffersController
from apps.uetopia.controllers.badges import BadgesController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="vouchers", version="v1", description="Vouchers API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class VouchersApi(remote.Service):
    @endpoints.method(VOUCHER_RESOURCE, VoucherResponse, path='create', http_method='POST', name='create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def create(self, request):
        """ Create a voucher - PROTECTED """
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VoucherResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return VoucherResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VoucherResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return VoucherResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()

        ## get the game
        game = gController.get_by_key_id(request.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return VoucherResponse(response_message='Error: Game not found.', response_successful=False)

        # make sure this user is the game owner
        if game.userKeyId != authorized_user.key.id():
            logging.info('User is not game owner.')
            return VoucherResponse(response_message='Error: User is not game owner.', response_successful=False)

        ## TODO  Get the offer associated with this voucher
        offer = offerController.get_by_key_id(request.offerKeyId)
        if not offer:
            logging.info('Offer not found.')
            return VoucherResponse(response_message='Error: Offer not found.', response_successful=False)


        # send out a discord alert to the game owner.
        # no bool for this since it should not really be optional
        if game.discord_webhook_admin:
            link = "https://ue4topia.appspot.com/#/games/%s" % (game.key.id())
            message = "New voucher created.  %s" %link
            http_auth = Http()
            headers = {"Content-Type": "application/json"}

            discord_data = { "embeds": [{"title": "New Voucher", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)

        # deal with possibly missing timestamps
        if request.starts:
            start_time = dateutil.parser.parse(request.starts)
        else:
            start_time = datetime.datetime.now()

        if request.ends:
            end_time = dateutil.parser.parse(request.ends)
        else:
            end_time = datetime.datetime.now() + datetime.timedelta(days = 1)

        voucher = voucherController.create(
            starts = start_time,
            ends = end_time,
            title = request.title,
            description = request.description,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            offerKeyId = offer.key.id(),
            offerTitle = offer.title,
            apiKey = voucherController.create_unique_api_key(),
            singleUse = request.singleUse,
            used = False,
            active = True
            )


        return VoucherResponse(response_message="Offer Created", response_successful=True, apiKey=voucher.apiKey)


    @endpoints.method(VOUCHER_COLLECTION_PAGE_RESOURCE, VoucherCollection, path='voucherCollectionGetPage', http_method='POST', name='collection.get.page')
    def voucherCollectionGetPage(self, request):
        """ Get a collection of vouchers """
        logging.info("voucherCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VoucherCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VoucherCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VoucherCollection(response_message='Error: No User Record Found. ', response_successful=False)

        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        #sort_order = request.sort_order
        #direction = request.direction

        offers = []

        ## if gameModeKeyId is supplied, get the ads for the game.  Verify game owner
        if request.gameKeyId:
            logging.info('gameKeyId found')

            game = gController.get_by_key_id(request.gameKeyId)
            if not game:
                logging.info('Game not found.')
                return VoucherCollection(response_message='Error: Game not found.', response_successful=False)

            if game.userKeyId != authorized_user.key.id():
                logging.info('Only the game owner can view offers')
                return VoucherCollection(response_message='Error: Only the game owner can view offers.', response_successful=False)


            if request.offerKeyId:
                logging.info('found offerKeyId')
                vouchers = voucherController.get_by_offerKeyId(int(request.offerKeyId))

            else:
                logging.info('did not find offerKeyId')
                vouchers = voucherController.get_by_gameKeyId(game.key.id())

        entity_list = []
        for voucher in vouchers:
            entity_list.append(VoucherResponse(
                key_id = voucher.key.id(),
                created= voucher.created.isoformat(' '),
                starts = voucher.starts.isoformat(' '),
                ends = voucher.ends.isoformat(' '),
                title = voucher.title,
                description = voucher.description,
                gameKeyId = voucher.gameKeyId,
                gameTitle = voucher.gameTitle,
                offerKeyId = voucher.offerKeyId,
                offerTitle = voucher.offerTitle,
                apiKey = voucher.apiKey,
                singleUse = voucher.singleUse,
                used = voucher.used,
                active = voucher.active,

            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = VoucherCollection(
            vouchers = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(VOUCHER_RESOURCE, VoucherResponse, path='voucherGet', http_method='POST', name='get')
    def voucherGet(self, request):
        """ Get a voucher """
        logging.info("voucherGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VoucherResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VoucherResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VoucherResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()

        ## Get the offer by key
        voucher = voucherController.get_by_key_id(request.key_id)
        if not voucher:
            logging.info('no voucher record found')
            return VoucherResponse(response_message='Error: No voucher Record Found. ', response_successful=False)

        ## check to see if the user is the owner of the game
        game = gController.get_by_key_id(voucher.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return VoucherResponse(response_message='Error: Game not found.', response_successful=False)

        if game.userKeyId != authorized_user.key.id():
            logging.info('Only the game owner can view vouchers details')
            return VoucherResponse(response_message='Error: Only the game owner can view offers.', response_successful=False)


        return VoucherResponse(
            key_id = voucher.key.id(),
            created= voucher.created.isoformat(' '),
            starts = voucher.starts.isoformat(' '),
            ends = voucher.ends.isoformat(' '),
            title = voucher.title,
            description = voucher.description,
            gameKeyId = voucher.gameKeyId,
            gameTitle = voucher.gameTitle,
            offerKeyId = voucher.offerKeyId,
            offerTitle = voucher.offerTitle,
            apiKey = voucher.apiKey,
            singleUse = voucher.singleUse,
            used = voucher.used,
            active = voucher.active,
        )

    @endpoints.method(VOUCHER_RESOURCE, VoucherResponse, path='redeem', http_method='POST', name='redeem')
    def redeem(self, request):
        """ Attempt to redeem a voucher - PROTECTED"""
        logging.info("redeem")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VoucherResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VoucherResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VoucherResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return VoucherResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()
        voucherClaimController = VoucherClaimsController()
        gamePlayerController = GamePlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()

        ## Get the offer by APIkey
        voucher = voucherController.get_by_api_key(request.apiKey)
        if not voucher:
            logging.info('no voucher record found')
            return VoucherResponse(response_message='Error: No voucher Record Found. ', response_successful=False)


        ## get the game player - create it if it does not exist
        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(voucher.gameKeyId, authorized_user.key.id())

        if not game_player:
            logging.info('game player not found.')

            ## create the game player
            ## it's safe to just create it.

            game_player = gamePlayerController.create(
                gameKeyId = voucher.gameKeyId,
                gameTitle = voucher.gameTitle,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                locked = False,
                online = True,
                rank = 1600,
                score = 0,
                #autoAuth = True,
                # = 100000,
                autoTransfer = True,
                firebaseUser = authorized_user.firebaseUser,
                picture = authorized_user.picture,
                lastServerClusterKeyId = None,
                groupKeyId = authorized_user.groupTagKeyId,
                groupTag = authorized_user.groupTag,
                showGameOnProfile = True
            )

        ## any other checks?

        ## TODO check to see if the voucher is single use
        ## if it is, is it redeemable?
        ## if so, queue up a redeem task

        if voucher.singleUse:
            logging.info('voucher is single use')

            voucher_memcache_key = "voucher:" + str(voucher.key.id())

            if voucherController.redeemable(voucher_memcache_key):
                logging.info('voucher is redeemable')

                voucherClaimController.create(
                    userKeyId = authorized_user.key.id(),
                    userTitle = authorized_user.title,
                    voucherKeyId = voucher.key.id(),
                    voucherTitle = voucher.title,
                    autoRefresh = request.autoRefresh
                )

                taskUrl='/task/voucher/attempt_redeem'
                taskqueue.add(url=taskUrl, queue_name='voucherAttemptRedeem', params={
                                                                                        "key_id": voucher.key.id()
                                                                                    }, countdown=2)
                return VoucherResponse(response_message='Attempting to redeem this Voucher - please stand by ', response_successful=True)

        else:
            logging.info('voucher is NOT single use - redeeming')

            ## don't create a claim.
            ## dont start a task
            ## just issue it.

            # we need the offer
            offer = offerController.get_by_api_key(voucher.offerKeyId)
            if not offer:
                logging.info('no offer record found')
                return VoucherResponse(response_message='Error: No offer Record Found. ', response_successful=False)

            ## make sure the user has enough balance
            if authorized_user.currencyBalance < offer.price:
                logging.info('user does not have enough balance')
                return VoucherResponse(response_message='Error: User does not have enough balance ', response_successful=False)

            ## only create a transaction for the game if non-zero
            recipient_transaction_key_id = None
            if offer.price > 0:
                logging.info('price is greater than zero - setting up transaction for the game')

                ## calculate the uetopia rake
                uetopia_rake = int(offer.price * UETOPIA_GROSS_PERCENTAGE_RAKE)
                logging.info("uetopia_rake: %s" % uetopia_rake)

                remaining_to_game = offer.price - uetopia_rake
                logging.info("remaining_to_game: %s" % remaining_to_game)

                description = "Offer purchase from: %s" %authorized_user.title
                recipient_transaction = transactionController.create(
                    amountInt = remaining_to_game,
                    amountIntGross = offer.price,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = offer.description,
                    ##userKeyId = authorized_user.key.id(),
                    ##firebaseUser = authorized_user.firebaseUser,
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
                    description = "Game Voucher Redeem Percentage from: %s" %authorized_user.title
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
            pushable = lockController.pushable("user:%s"%authorized_user.key.id())
            if pushable:
                logging.info('user pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": authorized_user.key.id()
                                                                                }, countdown=2)

            ## create the badge
            # calculate end date
            end_date = None
            autoRefresh = False
            if offer.timed:
                end_date = datetime.datetime.now() + datetime.timedelta(days=offer.duration_days, seconds=offer.duration_seconds)

                if offer.autoRefreshCapable and request.autoRefresh:
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
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
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
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                            'material_icon': MATERIAL_ICON_VOUCHER_REDEEM,
                                                                            'importance': 'md-primary',
                                                                            ## TODO this message can be more helpful
                                                                            'message_text': description,
                                                                            'action_button_color': 'primary',
                                                                            'action_button_sref': game_sref
                                                                            }, countdown = 1,)


        return VoucherResponse(response_message='Attempting to redeem this Voucher - please stand by ', response_successful=True)
