import logging
import datetime
import string
import json
from httplib2 import Http
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## CONTROLLERS
from apps.uetopia.controllers.vendor_types import VendorTypesController
from apps.uetopia.controllers.vendors import VendorsController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class CreateVendorHandler(BaseHandler):
    def post(self):
        """
        Create a vendor
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, userKeyId, vendorTypeKeyId, title, description, coordLocationX,coordLocationY,coordLocationZ
        """

        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()
        userController = UsersController()


        server = serverController.verify_signed_auth(self.request)

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                success = False,
            )
        else:
            logging.info('auth success')

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        if 'vendorTypeKeyId' not in jsonobject:
            logging.info('no vendorTypeKeyId found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendorTypeKeyId is required"
            )

        try:
            id_token = self.request.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')

        if id_token:
            logging.info("id_token: %s" %id_token)

            ## With a token we don't need all of this auto-auth garbage
            # Verify Firebase auth.
            #logging.info(self.request_state)

            claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
            if not claims:
                logging.error('Firebase Unauth')
                return self.render_json_response(
                    authorization = True,
                    player_authorized = False,
                    user_key_id = incoming_userid,
                    player_userid = incoming_userid,
                )

            authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

            if not authorized_user:
                logging.info('no user record found')
                return self.render_json_response(
                    authorization = True,
                    player_authorized = False,
                    user_key_id = incoming_userid,
                    player_userid = incoming_userid,
                )
        else:
            logging.info("No id_token found.  Doing it the old way - deprecated")

            if 'userKeyId' not in jsonobject:
                logging.info('no userKeyId found')
                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="userKeyId is required"
                )

            authorized_user = userController.get_by_key_id(int(jsonobject['userKeyId']))
            if not authorized_user:
                logging.info('no user found')
                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="user not found"
                )

        vendor_type = vendorTypeController.get_by_key_id(int(jsonobject['vendorTypeKeyId']))
        if not vendor_type:
            logging.info('no vendor_type found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendorType not found"
            )

        if not server.vendors_allowed:
            logging.info('vendors are not enabled on this server')
            ## TODO - send a chat message
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message='vendors are not enabled on this server'
            )

        if not server.player_created_vendors_allowed:
            if not server.userKeyId == authorized_user.key.id():
                logging.info('only the game owner can add vendors')
                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message='only the game owner can add vendors'
                )

        ## Check for DTID, set to none if missing
        if 'DTID' in jsonobject:
            logging.info('found vendor DTID')
            DTID = jsonobject['DTID']
        else:
            logging.info('DTID not found')
            DTID = None

        ## set the developer key/title
        developerUserKeyId = None
        developerUserTitle = None

        if server.userKeyId == authorized_user.key.id():
            developerUserKeyId = authorized_user.key.id()
            developerUserTitle = authorized_user.title
        else:
            ## look up the developer
            developer = userController.get_by_key_id(server.userKeyId)
            if developer:
                developerUserKeyId = developer.key.id()
                developerUserTitle = developer.title

        ## set bools
        buying = vendor_type.buyingMax > 0
        selling = vendor_type.sellingMax > 0

        vendor = vendorController.create(
            title = "New Vendor",
            description = "Detailed information about the objects I buy/sell",
            vendorTypeKeyId = vendor_type.key.id(),
            vendorTypeTitle = vendor_type.title,
            developerUserKeyId = developerUserKeyId,
            developerUserTitle = developerUserTitle,
            createdByUserKeyId = authorized_user.key.id(),
            createdByUserTitle = authorized_user.title,
            createdByUserFirebaseUser = authorized_user.firebaseUser,
            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,
            serverKeyId = server.key.id(),
            serverTitle = server.title,
            buyingMax = vendor_type.buyingMax,
            sellingMax = vendor_type.sellingMax,
            costToBuy = vendor_type.costToBuy,
            transactionTaxPercentageToServer = vendor_type.transactionTaxPercentageToServer,
            engineActorAsset = vendor_type.engineActorAsset,
            vendorCurrency = 0,
            coordLocationX = jsonobject['coordLocationX'],
            coordLocationY = jsonobject['coordLocationY'],
            coordLocationZ = jsonobject['coordLocationZ'],
            forwardVecX = jsonobject['forwardVecX'],
            forwardVecY = jsonobject['forwardVecY'],
            forwardVecZ = jsonobject['forwardVecZ'],
            buying = buying,
            selling = selling,
            thisVendorDTID = DTID
        )

        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor created",
            title = "New Vendor",
            description = "Detailed information about the objects I buy/sell",
            vendorKeyId = str(vendor.key.id()),
            vendorTypeKeyId = str(vendor_type.key.id()),
            coordLocationX = jsonobject['coordLocationX'],
            coordLocationY = jsonobject['coordLocationY'],
            coordLocationZ = jsonobject['coordLocationZ'],
            forwardVecX = jsonobject['forwardVecX'],
            forwardVecY = jsonobject['forwardVecY'],
            forwardVecZ = jsonobject['forwardVecZ'],
            createdByUserKeyId = str(authorized_user.key.id()),
            buyingMax = vendor_type.buyingMax,
            sellingMax = vendor_type.sellingMax,
            transactionTaxPercentageToServer = vendor_type.transactionTaxPercentageToServer,
            engineActorAsset = vendor_type.engineActorAsset,
        )
