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
from apps.uetopia.controllers.vendor_types import VendorTypesController
from apps.uetopia.controllers.vendors import VendorsController
from apps.uetopia.controllers.vendor_items import VendorItemsController
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

class WithdrawFromVendorHandler(BaseHandler):
    def post(self, vendorKeyId):
        """
        Withdraw currency from a vendor
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, userKeyId, vendorKeyId
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

        ## get the server player
        server_player = spController.get_server_user(server.key.id(), authorized_user.key.id())
        if not server_player:
            logging.info('no server player found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="server player not found"
            )


        vendor = vendorController.get_by_key_id(int(vendorKeyId))
        if not vendor:
            logging.info('no vendor found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendor not found"
            )

        transaction_amount = 0
        do_vendor_transaction = False
        description = "Vendor withdrawl"

        ## check if the vendor is owned by the player requesting
        if authorized_user.key.id() == vendor.createdByUserKeyId:
            logging.info('player is owner')

            ## Only proceed if the vendor is pushable
            pushable = lockController.pushable("vendor:%s"%vendor.key.id(), seconds=30)
            if pushable:
                logging.info('vendor is pushable')

                ## for the owner player, we just get the vendors currency.
                transaction_amount =  vendor.vendorCurrency

                ## we need two transactions to add to the queue.
                ## One for the server player

                recipient_transaction = transactionController.create(
                    amountInt = transaction_amount,
                    description = description,
                    vendorKeyId = vendor.key.id(),
                    vendorTitle = vendor.title,
                    userKeyId = authorized_user.key.id(),

                    ##  transactions are batched and processed all at once.
                    transactionType = "user",
                    transactionClass = "vendor withdrawal",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_VENDOR,
                    materialDisplayClass = "md-primary"
                )

                pushable = lockController.pushable("user:%s"%authorized_user.key.id())
                if pushable:
                    logging.info('user pushable')
                    taskUrl='/task/user/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                        "key_id": authorized_user.key.id()
                                                                                    }, countdown=2)




                transactionController.create(
                    amountInt = -transaction_amount,
                    description = description,
                    vendorKeyId = vendor.key.id(),
                    vendorTitle = vendor.title,
                    #serverPlayerKeyId = server_player.key.id(),

                    transactionType = "vendor",
                    transactionClass = "withdrawal",
                    transactionSender = True,
                    transactionRecipient = False,
                    recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_VENDOR,
                    materialDisplayClass = "md-accent"
                )

                logging.info('vendor pushable')
                taskUrl='/task/vendor/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='vendorTransactionProcess', params={
                                                                                        "key_id": vendor.key.id()
                                                                                    }, countdown=2)

                if vendor.discordWebhook:
                    ## do a discord push
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())
                    headers = {"Content-Type": "application/json"}

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Vendor: %s withdraw.  By %s " % (vendor.title, server_player.title)
                    ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Vendor Withdraw", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(vendor.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)

            else:
                logging.info('vendor not pushable - aborting')

                http_auth = Http()
                headers = {"Content-Type": "application/json"}

                textMessage = "> Cannot withdraw.  Please wait 30 seconds before withdraw attempts."

                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
                                        "userKeyId": "SYSTEM",
                                        "userTitle": "SYSTEM",
                                        #"chatMessageKeyId": chatMessageKeyId,
                                        #"chatChannelTitle": channel.title,
                                        #"chatChannelKeyId": channel.key.id(),
                                        "created":datetime.datetime.now().isoformat()
                })

                # push out to in-game clients via heroku
                # ignore if it's failing
                try:
                    URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, authorized_user.firebaseUser)
                    resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      chat_msg,
                                      headers=headers)

                    logging.info(resp)
                    logging.info(content)
                except:
                    logging.error('heroku error')

                return self.render_json_response(
                    authorization = True,
                    success=False,
                    response_message="vendor not pushable - aborting"
                )





        else:
            logging.info('player is not owner')

            ## for non-owners, we need to check all vendor items that are claimableAsCurrency
            claimable_items = vendorItemController.get_claimableAsCurrency_by_vendorKeyId_claimableForUserKeyId(vendor.key.id(), authorized_user.key.id())


            for claimable_item in claimable_items:
                logging.info('found claimable item')
                item_amount = claimable_item.quantityAvailable * claimable_item.pricePerUnit
                transaction_amount = transaction_amount + item_amount

                ## delete the item record.  we're done with it.
                vendorItemController.delete(claimable_item)


            ## set up a transaction

            recipient_transaction = transactionController.create(
                amountInt = transaction_amount,
                description = description,
                vendorKeyId = vendor.key.id(),
                vendorTitle = vendor.title,
                userKeyId = authorized_user.key.id(),

                ##  transactions are batched and processed all at once.
                transactionType = "user",
                transactionClass = "vendor withdrawal",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_VENDOR,
                materialDisplayClass = "md-primary"
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
                message = "Vendor: %s withdraw.  By %s " % (vendor.title, server_player.title)
                ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Vendor Withdraw", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(vendor.discordWebhook,
                                  "POST",
                                  data,
                                  headers=headers)


        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor withdraw completed",
            transaction_amount = transaction_amount,
            userKeyId = str(authorized_user.key.id())
        )
