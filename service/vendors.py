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

## endpoints v2 wants a "collection" so it can build the openapi files
#from api_collection import api_collection


from apps.uetopia.controllers.users import UsersController

## MODELS
from apps.uetopia.models.vendor_types import *
from apps.uetopia.models.vendors import *

## CONTROLLERS
from apps.uetopia.controllers.vendor_types import VendorTypesController
from apps.uetopia.controllers.vendors import VendorsController
from apps.uetopia.controllers.vendor_items import VendorItemsController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.servers import ServersController


from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

@endpoints.api(name="vendors", version="v1", description="Vendors API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class VendorsApi(remote.Service):
    @endpoints.method(VENDOR_TYPE_CREATE_RESOURCE, VendorTypeResponse, path='typeCreate', http_method='POST', name='type.create')
    def typeCreate(self, request):
        """ Create a vendor type - PROTECTED """
        logging.info("typeCreate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VendorTypeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorTypeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorTypeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return VendorTypeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)



        gamesController = GamesController()
        vendorTypeController = VendorTypesController()

        if not request.gameKeyId:
            logging.info('no gameKeyId found')
            return VendorTypeResponse(response_message="gameKeyId is required", response_successful=False)

        game = gamesController.get_by_key_id(int(request.gameKeyId))
        if not game:
            logging.info('no game found')
            return VendorTypeResponse(response_message="game not found", response_successful=False)

        if not game.userKeyId == authorized_user.key.id():
            logging.info('only the game owner can add vendor types')
            return VendorTypeResponse(response_message="only the game owner can add vendor types", response_successful=False)

        vendorTypeController.create(
            title = request.title,
            description = request.description,
            developerUserKeyId = authorized_user.key.id(),
            developerUserTitle = authorized_user.title,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            buyingMax = request.buyingMax,
            sellingMax = request.sellingMax,
            costToBuy = request.costToBuy,
            transactionTaxPercentageToServer = request.transactionTaxPercentageToServer,
            engineActorAsset = request.engineActorAsset
        )

        return VendorTypeResponse(response_message="Vendor Type Created", response_successful=True)

    @endpoints.method(VENDOR_TYPE_COLLECTION_PAGE_RESOURCE, VendorTypeCollection, path='typesCollectionGetPage', http_method='POST', name='type.collection.get.page')
    def typesCollectionGetPage(self, request):
        """ Get a collection of vendor types """
        logging.info("typesCollectionGetPage")

        """

        id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorTypeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorTypeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        """

        gamesController = GamesController()
        vendorTypeController = VendorTypesController()

        if not request.gameKeyId:
            return VendorTypeCollection(response_message="gameKeyId is required")

        game = gamesController.get_by_key_id(int(request.gameKeyId))
        if not game:
            return VendorTypeCollection(response_message="game not found", response_successful=False)

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        sort_order = request.sort_order
        direction = request.direction

        entities = vendorTypeController.get_by_gameKeyId(game.key.id())

        entity_list = []

        for entity in entities:
            entity_list.append(VendorTypeResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description
            ))

        response = VendorTypeCollection(
            vendor_types = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(VENDOR_TYPE_GET_RESOURCE, VendorTypeResponse, path='typeGet', http_method='POST', name='type.get')
    def typeGet(self, request):
        """ Get a single vendor type """
        logging.info("typeGet")

        """

        id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorTypeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorTypeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        """

        vendorTypeController = VendorTypesController()

        if not request.key_id:
            return VendorTypeResponse(response_message="key_id is required", response_successful=False)

        entity = vendorTypeController.get_by_key_id(int(request.key_id))

        return VendorTypeResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            buyingMax = entity.buyingMax,
            sellingMax = entity.sellingMax,
            costToBuy = entity.costToBuy,
            transactionTaxPercentageToServer = entity.transactionTaxPercentageToServer,
            engineActorAsset = entity.engineActorAsset,
            response_message='Success.  Vendor Type updated.',
            response_successful=True
        )

    @endpoints.method(VENDOR_TYPE_EDIT_RESOURCE, VendorTypeResponse, path='typeUpdate', http_method='POST', name='type.update')
    def typeUpdate(self, request):
        """ Update a vendor type - PROTECTED """
        logging.info("typeUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VendorTypeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorTypeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorTypeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return VendorTypeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        vendorTypeController = VendorTypesController()

        if not request.key_id:
            return VendorTypeResponse(response_message="key_id is required", response_successful=False)

        entity = vendorTypeController.get_by_key_id(int(request.key_id))

        if not entity.developerUserKeyId == authorized_user.key.id():
            return VendorTypeResponse(response_message="only the game owner can update vendor types", response_successful=False)

        entity.title = request.title
        entity.description = request.description
        entity.buyingMax = request.buyingMax
        entity.sellingMax = request.sellingMax
        entity.costToBuy = request.costToBuy
        entity.transactionTaxPercentageToServer = request.transactionTaxPercentageToServer
        entity.engineActorAsset = request.engineActorAsset

        vendorTypeController.update(entity)

        ## TODO update child vendors

        response = VendorTypeResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            response_message='Success.  Vendor Type updated.',
            response_successful=True
        )

        return response

    @endpoints.method(VENDOR_TYPE_GET_RESOURCE, VendorTypeResponse, path='typeDelete', http_method='POST', name='type.delete')
    def typeDelete(self, request):
        """ Delete a vendor type - PROTECTED """
        logging.info("typeDelete")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VendorTypeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorTypeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorTypeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return VendorTypeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        vendorTypeController = VendorTypesController()

        if not request.key_id:
            return VendorTypeResponse(response_message="key_id is required", response_successful=False)

        entity = vendorTypeController.get_by_key_id(int(request.key_id))

        if not entity.developerUserKeyId == authorized_user.key.id():
            return VendorTypeResponse(response_message="only the game owner can delete vendor types", response_successful=False)

        ## TODO check to see if there are existing vendors that use this type

        vendorTypeController.delete(entity)

        response = VendorTypeResponse(
            response_message='Success.  Vendor Type deleted.',
            response_successful=True
        )

        return response

    ########################### VENDORS
    @endpoints.method(VENDOR_CREATE_RESOURCE, VendorResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        """ Create a vendor - Non-working for testing only.  Create working vendors in-game."""
        logging.info("create")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VendorResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorResponse(response_message='Error: No User Record Found. ', response_successful=False)


        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()

        if not request.serverKeyId:
            logging.info('no serverKeyId found')
            return VendorResponse(response_message="serverKeyId is required", response_successful=False)

        server = serverController.get_by_key_id(int(request.serverKeyId))
        if not server:
            logging.info('no server found')
            return VendorResponse(response_message="server not found", response_successful=False)

        if not request.vendorTypeKeyId:
            logging.info('no vendorTypeKeyId found')
            return VendorResponse(response_message="vendorTypeKeyId is required", response_successful=False)

        vendor_type = vendorTypeController.get_by_key_id(int(request.vendorTypeKeyId))
        if not vendor_type:
            logging.info('no vendor_type found')
            return VendorResponse(response_message="vendor_type not found", response_successful=False)

        if not server.vendors_allowed:
            logging.info('vendors are not enabled on this server')
            return VendorResponse(response_message="vendors are not enabled on this server", response_successful=False)

        if not server.player_created_vendors_allowed:
            if not server.userKeyId == authorized_user.key.id():
                logging.info('only the game owner can add vendors')
                return VendorResponse(response_message="only the game owner can add vendors", response_successful=False)


        ## set the vendor DTID if provided
        if request.thisVendorDTID:
            logging.info('found vendor DTID')
            thisVendorDTID = request.thisVendorDTID
        else:
            logging.info('did not find vendor dtid')
            thisVendorDTID = None

        ## set the developer key/title
        developerUserKeyId = None
        developerUserTitle = None

        if server.userKeyId == authorized_user.key.id():
            developerUserKeyId = authorized_user.key.id()
            developerUserTitle = authorized_user.title
        else:
            ## look up the developer
            developer = UsersController().get_by_key_id(server.userKeyId)
            if developer:
                developerUserKeyId = developer.key.id()
                developerUserTitle = developer.title


        vendorController.create(
            title = request.title,
            description = request.description,
            vendorTypeKeyId = vendor_type.key.id(),
            vendorTypeTitle = vendor_type.title,
            developerUserKeyId = developerUserKeyId,
            developerUserTitle = developerUserTitle,
            createdByUserKeyId = authorized_user.key.id(),
            createdByUserTitle = authorized_user.title,
            createdByUserFirebaseUser = authorized_user.firebaseUser,
            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,
            buyingMax = request.buyingMax,
            sellingMax = request.sellingMax,
            costToBuy = request.costToBuy,
            transactionTaxPercentageToServer = request.transactionTaxPercentageToServer,
            engineActorAsset = request.engineActorAsset,
            vendorCurrency = 0,
            coordLocationX = 0,
            coordLocationY = 0,
            coordLocationZ = 0,
            buying = True,
            selling = True,
            thisVendorDTID = thisVendorDTID
        )

        return VendorResponse(response_message="Vendor Created", response_successful=True)

    @endpoints.method(VENDOR_COLLECTION_PAGE_RESOURCE, VendorCollection, path='collectionGetPage', http_method='POST', name='collection.get.page')
    def collectionGetPage(self, request):
        """ Get a collection of vendors """
        logging.info("collectionGetPage")


        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VendorCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorCollection(response_message='Error: No User Record Found. ', response_successful=False)

        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()

        if not request.serverKeyId:
            logging.info('no serverKeyId found')
            return VendorCollection(response_message="serverKeyId is required", response_successful=False)

        server = serverController.get_by_key_id(int(request.serverKeyId))
        if not server:
            logging.info('no server found')
            return VendorCollection(response_message="server not found", response_successful=False)

        if not server.userKeyId == authorized_user.key.id():
            logging.info('only the game owner can see the vendor list')
            return VendorCollection(response_message="only the game owner can see the vendor list", response_successful=False)

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        sort_order = request.sort_order
        direction = request.direction

        entities = vendorController.get_by_serverKeyId(server.key.id())

        entity_list = []

        for entity in entities:
            entity_list.append(VendorResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description
            ))

        response = VendorCollection(
            vendors = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(VENDOR_GET_RESOURCE, VendorResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a single vendor """
        logging.info("get")

        ## This request is coming from a user
        ## Server requests use the API handler.
        ## TODO combine logic into a shared function


        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return VendorResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return VendorResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return VendorResponse(response_message='Error: No User Record Found. ', response_successful=False)



        vendorController = VendorsController()
        vendorItemController = VendorItemsController()

        if not request.key_id:
            logging.info('key_id is required')
            return VendorResponse(response_message="key_id is required", response_successful=False)

        entity = vendorController.get_by_key_id(int(request.key_id))

        if not entity:
            logging.info('vendor not found')
            return VendorResponse(response_message="vendor not found", vendorKeyIdStr=str(request.key_id), response_successful=False)


        ## get for sale vendor items
        vendor_items = vendorItemController.get_selling_by_vendorKeyId(entity.key.id())

        items_to_return = []

        for vendor_item in vendor_items:
            items_to_return.append(
                VendorItemResponse(
                    key_id_str = str(vendor_item.key.id()),
                    title = vendor_item.title,
                    description = vendor_item.description,
                    quantityAvailable = vendor_item.quantityAvailable,
                    pricePerUnit = vendor_item.pricePerUnit,
                    blueprintPath = vendor_item.blueprintPath,
                    attributes = vendor_item.attributes,
                    selling = vendor_item.selling,
                    buyingOffer = vendor_item.buyingOffer,
                    buyingOfferExpires = "Unused",
                    claimable = False,
                    tier = vendor_item.tier
                )
            )

        bMyVendor = False
        vendorCurrency = 0

        if entity.createdByUserKeyId == authorized_user.key.id():
            logging.info('this is my vendor')
            bMyVendor = True
            vendorCurrency = entity.vendorCurrency

            vendor_items_offered = vendorItemController.get_buyingOffer_by_vendorKeyId(entity.key.id())

            for vendor_item in vendor_items_offered:
                items_to_return.append(
                    VendorItemResponse(
                        key_id_str = str(vendor_item.key.id()),
                        title = vendor_item.title,
                        description = vendor_item.description,
                        quantityAvailable = vendor_item.quantityAvailable,
                        pricePerUnit = vendor_item.pricePerUnit,
                        blueprintPath = vendor_item.blueprintPath,
                        attributes = vendor_item.attributes,
                        selling = vendor_item.selling,
                        buyingOffer = vendor_item.buyingOffer,
                        buyingOfferExpires = vendor_item.buyingOfferExpires.strftime("%Y-%m-%d %H:%M"),
                        claimable = False,
                        tier = vendor_item.tier
                    )
                )

        else:
            logging.info('this is not my vendor')
            ## for non-owners, we need to check all vendor items that are claimableAsCurrency
            claimable_items = vendorItemController.get_claimableAsCurrency_by_vendorKeyId_claimableForUserKeyId(entity.key.id(), authorized_user.key.id())

            ## first get items that are claimable as currency - Items that were purchased by the vendor owner
            for claimable_item in claimable_items:
                logging.info('found claimable as currency item')
                item_amount = claimable_item.quantityAvailable * claimable_item.pricePerUnit
                vendorCurrency = vendorCurrency + item_amount

            ## Next get items that are claimable as items - Items that were declined or timed out
            claimable_items = vendorItemController.get_claimableAsItem_by_vendorKeyId_claimableForUserKeyId(entity.key.id(), authorized_user.key.id())
            for claimable_item in claimable_items:
                logging.info('found claimable as item')
                items_to_return.append(
                    VendorItemResponse(
                        key_id_str = str(claimable_item.key.id()),
                        title = claimable_item.title,
                        description = claimable_item.description,
                        quantityAvailable = claimable_item.quantityAvailable,
                        pricePerUnit = claimable_item.pricePerUnit,
                        blueprintPath = claimable_item.blueprintPath,
                        attributes = claimable_item.attributes,
                        selling = claimable_item.selling,
                        buyingOffer = claimable_item.buyingOffer,
                        buyingOfferExpires = claimable_item.buyingOfferExpires.strftime("%Y-%m-%d %H:%M"),
                        claimable = True,
                        tier = vendor_item.tier
                    )
                )


        return VendorResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            vendorCurrency = vendorCurrency,
            items = items_to_return,
            bMyVendor = bMyVendor,
            discordWebhook = entity.discordWebhook,
            vendorKeyIdStr = str(entity.key.id()),
            response_message='Success.  Vendor returned.',
            response_successful=True
        )

    ####################### VENDOR ITEMS
