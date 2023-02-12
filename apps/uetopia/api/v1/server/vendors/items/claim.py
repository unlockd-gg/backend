import logging
import datetime
import string
import json
from httplib2 import Http
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine


## CONTROLLERS
from apps.uetopia.controllers.vendor_items import VendorItemsController
from apps.uetopia.controllers.vendor_types import VendorTypesController
from apps.uetopia.controllers.vendors import VendorsController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ClaimVendorItemHandler(BaseHandler):
    def post(self, vendorKeyId, vendorItemKeyId):
        """
        Buy a vendor item
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, quantity,
        """

        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()
        userController = UsersController()
        vendorItemController = VendorItemsController()
        lockController = TransactionLockController()
        spController = ServerPlayersController()
        transactionController = TransactionsController()


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

        vendor = vendorController.get_by_key_id(int(vendorKeyId))
        if not vendor:
            logging.info('no vendor found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendor not found"
            )



        ## get the vendor item
        vendor_item = vendorItemController.get_by_key_id(int(vendorItemKeyId))
        if not vendor_item:
            logging.info('no vendor item found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendor item not found"
            )


        if not vendor_item.claimableAsItem:
            logging.info('this item is not claimable')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendor item not claimable"
            )

        if vendor_item.claimableForUserKeyId != authorized_user.key.id():
            logging.info('user does not match claimableForUserKeyId')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="user does not match claimableForUserKeyId"
            )

        # set vars to return
        pricePerUnit = vendor_item.pricePerUnit
        blueprintPath = vendor_item.blueprintPath
        quantityAvailable = vendor_item.quantityAvailable
        attributes = vendor_item.attributes
        ## modify the vendor item or delete it

        if vendor.discordWebhook:
            ## do a discord push
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Vendor: %s item claimed: %s" %(vendor.title, vendor_item.title)
            ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
            discord_data = { "embeds": [{"title": "Vendor item claimed", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(vendor.discordWebhook,
                              "POST",
                              data,
                              headers=headers)

        vendorItemController.delete(vendor_item)

        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor item claimed",
            #title=title,
            #description = description,
            vendorKeyId = str(vendor.key.id()),
            userKeyId = str(authorized_user.key.id()),
            quantityAvailable = quantityAvailable,
            attributes = attributes,
            #selling = selling,
            #buyingOffer = buyingOffer,
            #buyingOfferUserKeyId = buyingOfferUserKeyId,
            #claimable = True,
            #claimableForUserKeyId = str(authorized_user.key.id()),
            blueprintPath = blueprintPath
            )
