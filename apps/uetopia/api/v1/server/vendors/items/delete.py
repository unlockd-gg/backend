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

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class DeleteVendorItemHandler(BaseHandler):
    def post(self, vendorKeyId, vendorItemKeyId):
        """
        Create a vendor item
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, userKeyId
        """

        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()
        userController = UsersController()
        vendorItemController = VendorItemsController()


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



        vendor_item = vendorItemController.get_by_key_id(int(vendorItemKeyId))
        if not vendor_item:
            logging.info('no vendor_item found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendor_item not found"
            )

        if vendor_item.vendorKeyId != vendor.key.id():
            logging.info('vendorKeyId does not match')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendorKeyId does not match"
            )

        if vendor_item.serverKeyId != server.key.id():
            logging.info('serverKeyId does not match')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="serverKeyId does not match"
            )

        ## check to see how we should handle the deletion.
        ## if it's an item listed by the owner of the vendor, we can delete it and return it to inventory.
        ## if it's an item listed by a different user, and that user is the one that listed it, it can be deleted and returned.

        if authorized_user.key.id() == vendor.createdByUserKeyId:
            logging.info('this user owns the vendor')

            if vendor_item.buyingOfferUserKeyId:
                logging.info('vendor owner cannot delete buying offers made by other users')
                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="vendor owner cannot delete buying offers made by other users"
                )

            ## DO DELETE
        else:
            logging.info('this user does not own the vendor')

            if authorized_user.key.id() != vendor_item.buyingOfferUserKeyId:
                logging.info('you can not delete buy offers created by other users.')
                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message='you can not delete buy offers created by other users.'
                )
            ## DO DELETE

        ## cache return values before delete so we can return them.
        title = vendor_item.title
        description = vendor_item.description
        vendorKeyId = vendor_item.vendorKeyId
        userKeyId = vendor_item.userKeyId

        quantityAvailable = vendor_item.quantityAvailable
        pricePerUnit = vendor_item.pricePerUnit
        attributes = vendor_item.attributes

        selling = vendor_item.selling

        buyingOffer = vendor_item.buyingOffer
        buyingOfferUserKeyId = vendor_item.buyingOfferUserKeyId
        buyingOfferUserTitle = vendor_item.buyingOfferUserTitle
        buyingOfferFirebaseUser = vendor_item.buyingOfferFirebaseUser

        claimable = vendor_item.claimable
        claimableForUserKeyId = vendor_item.claimableForUserKeyId
        claimableForFirebaseUser = vendor_item.claimableForFirebaseUser

        blueprintPath = vendor_item.blueprintPath

        vendorItemController.delete(vendor_item)

        if vendor.discordWebhook:
            ## do a discord push
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Vendor: %s item deleted: %s" %(vendor.title, title)
            ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
            discord_data = { "embeds": [{"title": "Vendor item deleted", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(vendor.discordWebhook,
                              "POST",
                              data,
                              headers=headers)

        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor item deleted",
            title=title,
            description = description,
            vendorKeyId = vendorKeyId,
            userKeyId = str(userKeyId),
            quantityAvailable = quantityAvailable,
            pricePerUnit = pricePerUnit,
            attributes = attributes,
            selling = selling,
            buyingOffer = buyingOffer,
            buyingOfferUserKeyId = buyingOfferUserKeyId,
            claimable = claimable,
            claimableForUserKeyId = claimableForUserKeyId,
            blueprintPath = blueprintPath
            )
