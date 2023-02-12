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

class CreateVendorItemHandler(BaseHandler):
    def post(self, vendorKeyId):
        """
        Create a vendor item
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, userKeyId, vendorKeyId, title, description, coordLocationX,coordLocationY,coordLocationZ
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



        ## check existing server items against limits
        if authorized_user.key.id() == vendor.createdByUserKeyId:
            logging.info('this item is being listed for sale')
            existing_sale_items = vendorItemController.get_selling_by_vendorKeyId(vendor.key.id())
            if len(existing_sale_items) >= vendor.sellingMax:
                logging.info('Cannot list this item.  The server is already at max selling capacity.')

                if vendor.discordWebhook:
                    ## do a discord push
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())
                    headers = {"Content-Type": "application/json"}

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Vendor: %s full. " % (vendor.title)
                    ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Vendor full", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(vendor.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)

                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="Cannot list this item.  The server is already at max selling capacity."
                )
            selling = True
            buyingOffer = False
            buyingOfferUserKeyId = None
            buyingOfferUserTitle = None
            buyingOfferFirebaseUser = None
            buyingOfferExpires = None
        else:
            logging.info('this item is being offered to buy')
            ## user is already valid.
            existing_buy_items = vendorItemController.get_buyingOffer_by_vendorKeyId(vendor.key.id())
            if len(existing_buy_items) >= vendor.sellingMax:
                logging.info('Cannot list this item.  The server is already at max buying capacity.')

                if vendor.discordWebhook:
                    ## do a discord push
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())
                    headers = {"Content-Type": "application/json"}

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Vendor: %s full. " % (vendor.title)
                    ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Vendor full", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(vendor.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)

                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="Cannot list this item.  The server is already at max buying capacity."
                )
            selling = False
            buyingOffer = True
            buyingOfferUserKeyId = authorized_user.key.id()
            buyingOfferUserTitle = authorized_user.title
            buyingOfferFirebaseUser = authorized_user.firebaseUser
            buyingOfferExpires = datetime.datetime.now() + VENDOR_OFFER_AUTO_EXPIRE_TIME


        if 'dataTableId' in jsonobject:
            dataTableId = jsonobject['dataTableId']
        else:
            dataTableId = None

        if 'tier' in jsonobject:
            tier = jsonobject['tier']
        else:
            tier = 0

        vendor_item = vendorItemController.create(
            title = jsonobject['title'],
            description = jsonobject['description'],
            vendorKeyId = vendor.key.id(),
            vendorTitle = vendor.title,
            vendorTypeKeyId = vendor.vendorTypeKeyId,
            vendorTypeTitle = vendor.vendorTypeTitle,
            gameKeyId = vendor.gameKeyId,
            gameTitle = vendor.gameTitle,
            serverKeyId = vendor.serverKeyId,
            serverTitle = vendor.serverTitle,
            userKeyId = vendor.createdByUserKeyId, ## this is the vendor owner
            userTitle = vendor.createdByUserTitle,
            firebaseUser = vendor.createdByUserFirebaseUser,

            quantityAvailable = jsonobject['quantity'],
            pricePerUnit = jsonobject['pricePerUnit'],
            attributes = jsonobject['attributes'],

            selling = selling,

            buyingOffer = buyingOffer,
            buyingOfferUserKeyId = buyingOfferUserKeyId,
            buyingOfferUserTitle = buyingOfferUserTitle,
            buyingOfferFirebaseUser = buyingOfferFirebaseUser,
            buyingOfferExpires = buyingOfferExpires,

            claimable = False,
            claimableForUserKeyId = None,
            claimableForFirebaseUser = None,

            #iconPath = jsonobject['iconPath'],
            blueprintPath = jsonobject['blueprintPath'],
            dataTableId = dataTableId,
            tier = tier
        )

        if vendor.discordWebhook:
            ## do a discord push
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Vendor: %s new item listed: %s " % (vendor.title, vendor_item.title)
            ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
            discord_data = { "embeds": [{"title": "Vendor new item listed", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(vendor.discordWebhook,
                              "POST",
                              data,
                              headers=headers)

        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor item created",
            )
