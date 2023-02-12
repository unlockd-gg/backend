import endpoints
import logging
import uuid
import urllib
import json
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

from apps.uetopia.models.offers import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController

from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.offers import OffersController
from apps.uetopia.controllers.vouchers import VouchersController
from apps.uetopia.controllers.badges import BadgesController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="offers", version="v1", description="Offers API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class OffersApi(remote.Service):
    @endpoints.method(OFFER_RESOURCE, OfferResponse, path='create', http_method='POST', name='create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def create(self, request):
        """ Create an offer - PROTECTED """
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return OfferResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return OfferResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return OfferResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return OfferResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()

        offerController = OffersController()

        if request.price < 0:
            logging.info('price cannot be negative')
            return OfferResponse(response_message='Error: Price cannot be negative.', response_successful=False)

        ## get the game
        game = gController.get_by_key_id(request.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return OfferResponse(response_message='Error: Game not found.', response_successful=False)

        # make sure this user is the game owner
        if game.userKeyId != authorized_user.key.id():
            logging.info('User is not game owner.')
            return OfferResponse(response_message='Error: User is not game owner.', response_successful=False)


        # send out a discord alert to the game owner.
        # no bool for this since it should not really be optional
        if game.discord_webhook_admin:
            link = "https://ue4topia.appspot.com/#/games/%s" % (game.key.id())
            message = "New offer submitted.  %s" %link
            http_auth = Http()
            headers = {"Content-Type": "application/json"}

            discord_data = { "embeds": [{"title": "New Offer", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)

        offer = offerController.create(
            duration_days = request.duration_days,
            duration_seconds = request.duration_seconds,
            title = request.title,
            description = request.description,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            offerType = request.offerType,
            tags = request.tags,
            icon_url = request.icon_url,
            price = request.price,
            requireVoucher = request.requireVoucher,
            visible = request.visible,
            active = request.active,
            timed = request.timed,
            autoRefreshCapable = request.autoRefreshCapable
            )

        ## update firebase
        taskUrl='/task/game/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game.key.id()}, countdown = 2,)


        return OfferResponse(response_message="Offer Created", response_successful=True)


    @endpoints.method(OFFER_COLLECTION_PAGE_RESOURCE, OfferCollection, path='offerCollectionGetPage', http_method='POST', name='collection.get.page')
    def offerCollectionGetPage(self, request):
        """ Get a collection of offers """
        logging.info("offerCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return OfferCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return OfferCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return OfferCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        offerController = OffersController()


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
                return OfferCollection(response_message='Error: Game not found.', response_successful=False)

            if game.userKeyId != authorized_user.key.id():
                logging.info('Only the game owner can view offers')
                return OfferCollection(response_message='Error: Only the game owner can view offers.', response_successful=False)

            offers = offerController.get_by_gameKeyId(game.key.id())

        entity_list = []
        for offer in offers:
            entity_list.append(OfferResponse(
                key_id = offer.key.id(),
                created= offer.created.isoformat(' '),
                title = offer.title,
                description = offer.description,
                gameKeyId = offer.gameKeyId,
                gameTitle = offer.gameTitle,
                offerType = offer.offerType,
                tags = offer.tags,
                icon_url = offer.icon_url,
                price = offer.price,
                requireVoucher = offer.requireVoucher,
                visible = offer.visible,
                active = offer.active,
                timed = offer.timed,
                autoRefreshCapable = offer.autoRefreshCapable,
                duration_days = offer.duration_days,
                duration_seconds = offer.duration_seconds
            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = OfferCollection(
            offers = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(OFFER_RESOURCE, OfferResponse, path='offerGet', http_method='POST', name='get')
    def offerGet(self, request):
        """ Get an offer """
        logging.info("offerGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return OfferResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return OfferResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return OfferResponse(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()
        badgeController = BadgesController()

        ## if a voucherKey was supplied, use that to look up the connected offer
        if request.voucherKey:
            logging.info('looking up from voucherKey')
            voucher = voucherController.get_by_api_key(request.voucherKey)
            if not voucher:
                logging.info('voucher not found')
                return OfferResponse(response_message='Error: No Voucher Record Found. ', response_successful=False)

            ## Get the offer by key
            offer = offerController.get_by_key_id(voucher.offerKeyId)
            if not offer:
                logging.info('no offer record found')
                return OfferResponse(response_message='Error: No offer Record Found. ', response_successful=False)

            ## check to see if the user already has this offer in badges
            existing_badge = badgeController.get_by_offerKeyId_userKeyId(offer.key.id(), authorized_user.key.id() )
            found_existing_badge = False
            if existing_badge:
                logging.info('found an existing badge')
                found_existing_badge = True


            return OfferResponse(
                key_id = offer.key.id(),
                title = offer.title,
                description = offer.description,
                gameKeyId = offer.gameKeyId,
                gameTitle = offer.gameTitle,
                offerType = offer.offerType,
                tags = offer.tags,
                icon_url = offer.icon_url,
                price = offer.price,
                requireVoucher = offer.requireVoucher,
                visible = offer.visible,
                active = offer.active,
                timed = offer.timed,
                autoRefreshCapable = offer.autoRefreshCapable,
                duration_days = offer.duration_days,
                duration_seconds = offer.duration_seconds,
                existingBadge = found_existing_badge,
                response_message='Found available offer',
                response_successful=True
            )



        ## Get the offer by key
        offer = offerController.get_by_key_id(request.key_id)
        if not offer:
            logging.info('no offer record found')
            return OfferResponse(response_message='Error: No offer Record Found. ', response_successful=False)

        ## if the offer is visible active and does not require a voucher, anyone can view it.
        if offer.active and offer.visible and not offer.requireVoucher:
            logging.info('publicly viewable offer')

            return OfferResponse(
                key_id = offer.key.id(),
                title = offer.title,
                description = offer.description,
                gameKeyId = offer.gameKeyId,
                gameTitle = offer.gameTitle,
                offerType = offer.offerType,
                tags = offer.tags,
                icon_url = offer.icon_url,
                price = offer.price,
                requireVoucher = offer.requireVoucher,
                visible = offer.visible,
                active = offer.active,
                timed = offer.timed,
                autoRefreshCapable = offer.autoRefreshCapable,
                duration_days = offer.duration_days,
                duration_seconds = offer.duration_seconds,
                response_successful=True
            )

        else:

            ## check to see if the user is the owner of the game
            game = gController.get_by_key_id(offer.gameKeyId)
            if not game:
                logging.info('Game not found.')
                return OfferResponse(response_message='Error: Game not found.', response_successful=False)

            if game.userKeyId != authorized_user.key.id():
                logging.info('Only the game owner can view offers')
                return OfferResponse(response_message='Error: Only the game owner can view offers.', response_successful=False)


            return OfferResponse(
                key_id = offer.key.id(),
                title = offer.title,
                description = offer.description,
                gameKeyId = offer.gameKeyId,
                gameTitle = offer.gameTitle,
                offerType = offer.offerType,
                tags = offer.tags,
                icon_url = offer.icon_url,
                price = offer.price,
                requireVoucher = offer.requireVoucher,
                visible = offer.visible,
                active = offer.active,
                timed = offer.timed,
                autoRefreshCapable = offer.autoRefreshCapable,
                duration_days = offer.duration_days,
                duration_seconds = offer.duration_seconds,
                response_successful=True
            )


    @endpoints.method(OFFER_RESOURCE, OfferResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update an offer """
        logging.info("update")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return OfferResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return OfferResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return OfferResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return OfferResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()

        offerController = OffersController()
        ## get the requested ad

        requested_offer = offerController.get_by_key_id(request.key_id)

        if not requested_offer:
            logging.info('requested offer not found')
            return OfferResponse(response_message='Error: No offer Found. ', response_successful=False)

        ## check to see if the user is the owner of the game
        game = gController.get_by_key_id(requested_offer.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return OfferResponse(response_message='Error: Game not found.', response_successful=False)

        if game.userKeyId != authorized_user.key.id():
            logging.info('Only the game owner can view offers')
            return OfferResponse(response_message='Error: Only the game owner can update offers.', response_successful=False)



        requested_offer.duration_days = request.duration_days
        requested_offer.duration_seconds = request.duration_seconds
        requested_offer.title = request.title
        requested_offer.description = request.description
        requested_offer.offerType = request.offerType
        requested_offer.tags = request.tags
        requested_offer.icon_url = request.icon_url
        requested_offer.price = request.price
        requested_offer.requireVoucher = request.requireVoucher
        requested_offer.visible = request.visible
        requested_offer.active = request.active
        requested_offer.timed = request.timed
        requested_offer.autoRefreshCapable = request.autoRefreshCapable

        offerController.update(requested_offer)

        ## update firebase
        taskUrl='/task/game/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game.key.id()}, countdown = 2,)

        return OfferResponse(response_message='Success.  Offer updated.', response_successful=True)

    @endpoints.method(OFFER_RESOURCE, OfferResponse, path='claim', http_method='POST', name='claim')
    def claim(self, request):
        """ Claim an offer - PROTECTED """
        logging.info("offerGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return OfferResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return OfferResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return OfferResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return OfferResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()
        badgeController = BadgesController()
        gamePlayerController = GamePlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()


        ## Get the offer by key
        offer = offerController.get_by_key_id(request.key_id)
        if not offer:
            logging.info('no offer record found')
            return OfferResponse(response_message='Error: No offer Record Found. ', response_successful=False)

        ## check to see if the user already has this offer in badges
        existing_badge = badgeController.get_by_offerKeyId_userKeyId(offer.key.id(), authorized_user.key.id() )
        found_existing_badge = False
        if existing_badge:
            logging.info('found an existing badge')
            found_existing_badge = True
            return OfferResponse(response_message='Error: You already have an active badge for this offer. ', response_successful=False)


        ## if the offer is visible active and does not require a voucher, anyone can view it.
        if offer.active and offer.visible and not offer.requireVoucher:
            logging.info('publicly viewable offer - claiming')

            ## make sure the user has enough balance
            if authorized_user.currencyBalance < offer.price:
                logging.info('user does not have enough balance')
                return OfferResponse(response_message='Error: User does not have enough balance ', response_successful=False)

            ## get the game player - create it if it does not exist
            game_player = gamePlayerController.get_by_gameKeyId_userKeyId(offer.gameKeyId, authorized_user.key.id())

            if not game_player:
                logging.info('game player not found.')

                ## create the game player
                ## it's safe to just create it.

                game_player = gamePlayerController.create(
                    gameKeyId = offer.gameKeyId,
                    gameTitle = offer.gameTitle,
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
                    description = "Game Offer Claim Percentage from: %s" %authorized_user.title
                    recipient_transaction = transactionController.create(
                        amountInt = uetopia_rake,
                        description = description,
                        #serverKeyId = server.key.id(),
                        #serverTitle = server.title,
                        gameKeyId = offer.gameKeyId,
                        gameTitle = offer.gameTitle,
                        transactionType = "uetopia",
                        transactionClass = "game offer claim rake",
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
            description = "Claimed Offer: %s" %offer.title
            transactionController.create(
                amountInt = -offer.price,
                ##amount = ndb.FloatProperty(indexed=False) # for display
                ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                ##newBalance = ndb.FloatProperty(indexed=False) # for display
                description = offer.description,
                userKeyId = authorized_user.key.id(),
                firebaseUser = authorized_user.firebaseUser,
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
                #voucherKeyId = voucher.key.id(),
                #voucherTitle = voucher.title,
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

        else:
            logging.info('offer not redeemable')


        return OfferResponse(response_message='Attempting to redeem this Voucher - please stand by ', response_successful=True)
