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

class BuyVendorItemHandler(BaseHandler):
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



        ## get the server player
        server_player = spController.get_server_user(server.key.id(), authorized_user.key.id())
        if not server_player:
            return self.render_json_response(
                authorization = True,
                success=False
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

        ## make sure the quantity makes sense
        requested_quantiy = int(jsonobject['quantity'])
        if requested_quantiy < 1:
            logging.info('requested quanity must be greater than 1')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="requested quanity must be greater than 1"
            )

        item_quantity_buyout = False

        if requested_quantiy >= vendor_item.quantityAvailable:
            logging.info('requested quantity was too high, setting it to available quantity')
            requested_quantiy = vendor_item.quantityAvailable
            item_quantity_buyout = True

        purchase_price = requested_quantiy * vendor_item.pricePerUnit

        ## make sure the player has enough balance to cover it
        if authorized_user.currencyBalance < purchase_price:
            logging.info('user does not have enough balance to cover it')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="user does not have enough balance"
            )

        ## distinguish between an item listed for sale, and an offer
        ## WE need to treat them differently

        if vendor_item.selling:
            logging.info('this item is listed as selling')

            ## TODO any other checks needed?

            ## make transactions, and queue them up

            description = server_player.userTitle + " bought " + str(requested_quantiy) + "x " + vendor_item.title

            ## we need two transactions to add to the queue.
            ## One for the vendor

            recipient_transaction = transactionController.create(
                amountInt = purchase_price,
                description = description,
                vendorKeyId = vendor.key.id(),
                vendorTitle = vendor.title,
                #serverPlayerKeyId = server_player.key.id(),

                ##  transactions are batched and processed all at once.
                transactionType = "vendor",
                transactionClass = "purchase",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_VENDOR,
                materialDisplayClass = "md-primary"
            )
            ## One for the user

            description = "Bought " + str(requested_quantiy) + "x " + vendor_item.title

            transactionController.create(
                amountInt = -purchase_price,
                description = description,
                vendorKeyId = vendor.key.id(),
                vendorTitle = vendor.title,
                userKeyId = authorized_user.key.id(),

                transactionType = "user",
                transactionClass = "purchase",
                transactionSender = True,
                transactionRecipient = False,
                recipientTransactionKeyId = recipient_transaction.key.id(),
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_VENDOR,
                materialDisplayClass = "md-accent"
            )

            ## then start tasks to process them

            ## only start pushable tasks.  If they are not pushable, there is already a task running.
            pushable = lockController.pushable("vendor:%s"%vendor.key.id())
            if pushable:
                logging.info('vendor pushable')
                taskUrl='/task/vendor/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='vendorTransactionProcess', params={
                                                                                        "key_id": vendor.key.id()
                                                                                    }, countdown=2)

            pushable = lockController.pushable("user:%s"%authorized_user.key.id())
            if pushable:
                logging.info('user pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": authorized_user.key.id()
                                                                                }, countdown=2)

            # set vars to return
            pricePerUnit = vendor_item.pricePerUnit
            blueprintPath = vendor_item.blueprintPath
            attributes = vendor_item.attributes
            ## modify the vendor item or delete it

            if item_quantity_buyout:
                vendorItemController.delete(vendor_item)
            else:
                vendor_item.quantityAvailable = vendor_item.quantityAvailable - requested_quantiy
                vendorItemController.update(vendor_item)

            if vendor.discordWebhook:
                ## do a discord push
                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                headers = {"Content-Type": "application/json"}

                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = description
                ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Vendor sale", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(vendor.discordWebhook,
                                  "POST",
                                  data,
                                  headers=headers)


            return self.render_json_response(
                authorization = True,
                success=True,
                response_message="vendor item bought",
                #title=title,
                attributes = attributes,
                vendorKeyId = str(vendor.key.id()),
                userKeyId = str(authorized_user.key.id()),
                quantityBought = requested_quantiy,
                pricePerUnit = pricePerUnit,
                #selling = selling,
                #buyingOffer = buyingOffer,
                #buyingOfferUserKeyId = buyingOfferUserKeyId,
                #claimable = True,
                #claimableForUserKeyId = str(authorized_user.key.id()),
                blueprintPath = blueprintPath
                )

        elif vendor_item.buyingOffer:
            logging.info('this item is listed as offer')

            ## in this case, we don't delete the item, only mark it as claimed.
            ## we're using the claimed item record to facilitate user balance
            ## if the vendor owner did not buy the full stack, create a new item copy, and adjust quantities

            ## make sure the user is the vendor owner
            if authorized_user.key.id() != vendor.createdByUserKeyId:
                logging.info('only the vendor owner can buy offers')
                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="only the vendor owner can buy offers"
                )

            if item_quantity_buyout == False:
                logging.info('Not buying the full stack - splitting it')

                remaining_quantity = vendor_item.quantityAvailable - requested_quantiy

                remaining_item_listing = vendorItemController.create(
                    title = vendor_item.title,
                    description = vendor_item.description,
                    vendorKeyId = vendor_item.vendorKeyId,
                    vendorTitle = vendor_item.vendorTitle,
                    vendorTypeKeyId = vendor_item.vendorTypeKeyId,
                    vendorTypeTitle = vendor_item.vendorTypeTitle,
                    gameKeyId = vendor_item.gameKeyId,
                    gameTitle = vendor_item.gameTitle,
                    serverKeyId = vendor_item.serverKeyId,
                    serverTitle = vendor_item.serverTitle,
                    userKeyId = vendor_item.userKeyId,
                    userTitle = vendor_item.userTitle,
                    firebaseUser = vendor_item.firebaseUser,
                    quantityAvailable = remaining_quantity,
                    pricePerUnit = vendor_item.pricePerUnit,
                    selling = vendor_item.selling,
                    buyingOffer = vendor_item.buyingOffer,
                    buyingOfferUserKeyId = vendor_item.buyingOfferUserKeyId,
                    buyingOfferUserTitle = vendor_item.buyingOfferUserTitle,
                    buyingOfferFirebaseUser = vendor_item.buyingOfferFirebaseUser,
                    buyingOfferExpires = vendor_item.buyingOfferExpires,
                    claimable = False,
                    claimableForUserKeyId = None,
                    claimableForFirebaseUser = None,
                    blueprintPath = vendor_item.blueprintPath,
                )

                # set vars to return
                pricePerUnit = vendor_item.pricePerUnit
                blueprintPath = vendor_item.blueprintPath

                ## reduce the quantity on the original item, and mark it as bought
                vendor_item.quantityAvailable = vendor_item.quantityAvailable - remaining_quantity
                vendor_item.buyingOffer = False
                vendor_item.claimable = True
                vendor_item.claimableAsCurrency = True
                vendor_item.claimableForUserKeyId = vendor_item.buyingOfferUserKeyId
                vendor_item.claimableForFirebaseUser = vendor_item.buyingOfferFirebaseUser

                vendorItemController.update(vendor_item)

            else:
                logging.info('Buying the full stack - marking it as currency claimable')

                # set vars to return
                pricePerUnit = vendor_item.pricePerUnit
                blueprintPath = vendor_item.blueprintPath

                ## mark it as bought

                vendor_item.buyingOffer = False
                vendor_item.claimable = True
                vendor_item.claimableAsCurrency = True
                vendor_item.claimableForUserKeyId = vendor_item.buyingOfferUserKeyId
                vendor_item.claimableForFirebaseUser = vendor_item.buyingOfferFirebaseUser

                vendorItemController.update(vendor_item)



            ## transactions
            ## we just need one actually. The other transaction will get created when the user claims the item at the vendor

            description = "Bought " + str(requested_quantiy) + "x " + vendor_item.title

            transactionController.create(
                amountInt = -purchase_price,
                description = description,
                vendorKeyId = vendor.key.id(),
                vendorTitle = vendor.title,
                userKeyId = authorized_user.key.id(),

                transactionType = "user",
                transactionClass = "purchase",
                transactionSender = True,
                transactionRecipient = False,
                recipientTransactionKeyId = None,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_VENDOR,
                materialDisplayClass = "md-accent"
            )

            pushable = lockController.pushable("user:%s"%authorized_user.key.id())
            if pushable:
                logging.info('user pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": authorized_user.key.id()
                                                                                }, countdown=2)

            if vendor.discordWebhook:
                ## do a discord push
                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                headers = {"Content-Type": "application/json"}

                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = description
                ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Vendor sale", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(vendor.discordWebhook,
                                  "POST",
                                  data,
                                  headers=headers)

            return self.render_json_response(
                authorization = True,
                success=True,
                response_message="vendor item bought",
                #title=title,
                #description = description,
                vendorKeyId = str(vendor.key.id()),
                userKeyId = str(authorized_user.key.id()),
                quantityBought = requested_quantiy,
                pricePerUnit = pricePerUnit,
                #selling = selling,
                #buyingOffer = buyingOffer,
                #buyingOfferUserKeyId = buyingOfferUserKeyId,
                #claimable = True,
                #claimableForUserKeyId = str(authorized_user.key.id()),
                blueprintPath = blueprintPath
                )



        else:
            logging.info('unknown item state')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="unknown item state"
            )
