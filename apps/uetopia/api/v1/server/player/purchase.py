import logging
import datetime
import string
import json
from httplib2 import Http

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.store_item_consignments import StoreItemConsignmentsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class serverPlayerPurchaseHandler(BaseHandler):
    def post(self, userid):
        """
        transfer CRED from a server player to a server
        Requires http headers:  Key, Sign
        Requires JSON parameters:  nonce, amount, description, itemName
        """

        serverController = ServersController()
        ucontroller = UsersController()
        spController = ServerPlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        storeItemConsignmentController = StoreItemConsignmentsController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

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
                    userKeyId = userid,
                    player_userid = userid,
                    error_message = 'Firebase Unauth',
                )

            authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

            if not authorized_user:
                logging.info('no user record found')
                return self.render_json_response(
                    authorization = True,
                    player_authorized = False,
                    userKeyId = userid,
                    player_userid = userid,
                    error_message = 'no user record found',
                )
        else:
            logging.info("No id_token found.  NOT Doing it the old way - deprecated")

            return self.render_json_response(
                authorization = True,
                success=False,
                error_message = "No id_token found.  NOT Doing it the old way - deprecated",
                ## TODO we're going to need some more info in here, so we can properly respond to this
                ## maybe some sort of string var or two to help identify what should happen in-game
                #amount = amountInt,
                #userKeyId = userid,
                #description = jsonobject['description'],
                #itemName = jsonobject['itemName']
            )

        ## get the server player
        #server_player = spController.get_server_user(server.key.id(), int(userid))
        #if not server_player:
        #    return self.render_json_response(
        #        authorization = True,
        #        success=False
        #    )

        ## only permit purchases if the user is pushable
        pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        if not pushable:
            logging.info('user not pushable')
            return self.render_json_response(
                authorization = True,
                success=False,
                userKeyId = userid,
                error_message = "Purchase cooldown.  Wait 10 sec. "
            )



        ## we use json now

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)
        ## encryption = jsonobject["encryption"]

        if 'amount' not in jsonobject:
            logging.info(" amount was not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                userKeyId = userid
            )

        if 'description' not in jsonobject:
            logging.info(" description not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                userKeyId = userid,
                error_message = "description not found in json"
            )

        if 'itemName' not in jsonobject:
            logging.info(" itemName not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                userKeyId = userid,
                error_message = "itemName not found in json"
            )

        ## make sure the player has enough balance to cover it
        if authorized_user.currencyBalance < jsonobject['amount']:
            logging.info('user does not have enough balance to cover it')
            return self.render_json_response(
                authorization = True,
                success=False,
                userKeyId = userid,
                error_message = "You do not have enough balance to make this purchase."
            )


        ## TODO any other checks needed?

        ## make transactions, and queue them up
        transactionController = TransactionsController()

        groupController = GroupsController()

        amountInt = jsonobject['amount']

        ## calculate the uetopia rake
        uetopia_rake = int(amountInt * UETOPIA_GROSS_PERCENTAGE_RAKE)
        logging.info("uetopia_rake: %s" % uetopia_rake)

        remaining_amount_to_server = amountInt - uetopia_rake
        logging.info("remaining_amount_to_server: %s" % remaining_amount_to_server)

        if 'consignmentId' in jsonobject:
            logging.info('found consignmentId in json')

            # consignmentId might not exist
            # old clients will just send ''
            # wrapping it in a try for now - there may be a better way to handle this.  TODO - revisit this.
            consignmentId = 0
            try:
                consignmentId = int(jsonobject['consignmentId'])
            except:
                logging.info('consignmentID was unable to be converted to an integer')

            if consignmentId:
                consignment = storeItemConsignmentController.get_by_key_id(consignmentId)
                if consignment:
                    logging.info('found consignment record')

                    ## Only process consignments if the server has a positive balance
                    if server.serverCurrency >= 0:

                        if consignment.group:
                            logging.info('this is a group consignment')
                            ## get the group - We need the discord stuff
                            group = groupController.get_by_key_id(consignment.groupKeyId)
                            if group:
                                logging.info('found group')
                                ## set up a transaction for the group consignment recipient
                                ## we shouldn't need to check the group - it should have been checked on creation/edit
                                description = "Consignment payment from: %s : %s" %(server.gameTitle, consignment.title)
                                consignment_recipient_transaction = transactionController.create(
                                    amountInt = consignment.pricePerUnit,
                                    amountIntGross = consignment.pricePerUnit,
                                    ##amount = ndb.FloatProperty(indexed=False) # for display
                                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                                    description = description,
                                    ##userKeyId = authorized_user.key.id(),
                                    ##firebaseUser = authorized_user.firebaseUser,
                                    ##targetUserKeyId = ndb.IntegerProperty()
                                    groupKeyId = consignment.groupKeyId,
                                    groupTitle = consignment.groupTitle,

                                    ##  transactions are batched and processed all at once.
                                    transactionType = "group",
                                    transactionClass = "consignment",
                                    transactionSender = False,
                                    transactionRecipient = True,
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_DONATE,
                                    materialDisplayClass = "md-primary"
                                )

                                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                                pushable = lockController.pushable("group:%s"%consignment.groupKeyId)
                                if pushable:
                                    logging.info('group pushable')
                                    taskUrl='/task/group/transaction/process'
                                    taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                                            "key_id": consignment.groupKeyId
                                                                                                        }, countdown=2)

                                ## the server also needs a withdrawal transaction here
                                description = "Consignment paid to group: %s : %s" %(consignment.groupTitle, consignment.title)
                                transactionController.create(
                                    amountInt = -consignment.pricePerUnit,
                                    description = description,
                                    serverKeyId = server.key.id(),
                                    serverTitle = server.title,

                                    transactionType = "server",
                                    transactionClass = "consignment",
                                    transactionSender = True,
                                    transactionRecipient = False,
                                    recipientTransactionKeyId = consignment_recipient_transaction.key.id(),
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_REWARD,
                                    materialDisplayClass = "md-accent"
                                )

                                ## the server will get a process transaction task below

                                ## also send a discord push if configured
                                ## DIscord message to the group if configured
                                if group.discord_webhook and group.discord_subscribe_consignments:
                                    link = "https://ue4topia.appspot.com/#/game/%s" % (server.gameKeyId)
                                    message = "%s %s %s" %(consignment.pricePerUnit, consignment.title, link)
                                    http_auth = Http()
                                    headers = {"Content-Type": "application/json"}

                                    discord_data = { "embeds": [{"title": "New Consignment Purchase", "description": message}] }
                                    data=json.dumps(discord_data)
                                    resp, content = http_auth.request(group.discord_webhook,
                                                      "POST",
                                                      data,
                                                      headers=headers)


                        else:
                            logging.info('this is a user consignment')

                            # get the user - we need the discord stuff
                            consignment_user = ucontroller.get_by_key_id(consignment.userKeyId)
                            if consignment_user:
                                logging.info('Got consignment user')

                                description = "Consignment payment from: %s : %s" %(server.gameTitle, consignment.title)
                                consignment_recipient_transaction = transactionController.create(
                                    amountInt = consignment.pricePerUnit,
                                    amountIntGross = consignment.pricePerUnit,
                                    description = description,
                                    userKeyId = consignment.userKeyId,

                                    ##  transactions are batched and processed all at once.
                                    transactionType = "user",
                                    transactionClass = "consignment",
                                    transactionSender = False,
                                    transactionRecipient = True,
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_DONATE,
                                    materialDisplayClass = "md-primary"
                                )

                                ## this is possibly a different user than below, so trying to get a task running here
                                pushable = lockController.pushable("user:%s"%consignment.userKeyId)
                                if pushable:
                                    logging.info('user pushable')
                                    taskUrl='/task/user/transaction/process'
                                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                        "key_id": consignment.userKeyId
                                                                                                    }, countdown=2)

                                ## the server also needs a withdrawal transaction here
                                description = "Consignment paid to group: %s : %s" %(consignment.groupTitle, consignment.title)
                                transactionController.create(
                                    amountInt = -consignment.pricePerUnit,
                                    description = description,
                                    serverKeyId = server.key.id(),
                                    serverTitle = server.title,

                                    transactionType = "server",
                                    transactionClass = "consignment",
                                    transactionSender = True,
                                    transactionRecipient = False,
                                    recipientTransactionKeyId = consignment_recipient_transaction.key.id(),
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_REWARD,
                                    materialDisplayClass = "md-accent"
                                )

                                ## the server will get a process transaction task below

                                ## DIscord message to the user if configured
                                if consignment_user.discord_webhook and consignment_user.discord_subscribe_consignments:
                                    link = "https://ue4topia.appspot.com/#/game/%s" % (server.gameKeyId)
                                    message = "%s %s %s" %(consignment.pricePerUnit, consignment.title, link)
                                    http_auth = Http()
                                    headers = {"Content-Type": "application/json"}

                                    discord_data = { "embeds": [{"title": "New Consignment Purchase", "description": message}] }
                                    data=json.dumps(discord_data)
                                    resp, content = http_auth.request(consignment_user.discord_webhook,
                                                      "POST",
                                                      data,
                                                      headers=headers)

                    else:
                        logging.error('this server had a negative balance and tried to process a consignment')

                        ## TODO send a discord message to the game owner






        ## we need two transactions to add to the queue.
        ## One for the server
        #description = "Reward from: %s" %server.title
        description = "Purchase by: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = remaining_amount_to_server,
            amountIntGross = amountInt,
            description = description,
            serverKeyId = server.key.id(),
            serverTitle = server.title,
            #serverPlayerKeyId = server_player.key.id(),

            ##  transactions are batched and processed all at once.
            transactionType = "server",
            transactionClass = "purchase",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_PURCHASE,
            materialDisplayClass = "md-primary"
        )
        ## One for the user

        description = server.gameTitle + ": " + server.title + ": " + jsonobject['description']
        transactionController.create(
            amountInt = -amountInt,
            description = description,
            serverKeyId = server.key.id(),
            serverTitle = server.title,
            userKeyId = authorized_user.key.id(),

            transactionType = "user",
            transactionClass = "purchase",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_PURCHASE,
            materialDisplayClass = "md-accent"
        )

        ## then start tasks to process them

        ## only start pushable tasks.  If they are not pushable, there is already a task running.
        pushable = lockController.pushable("server:%s"%server.key.id())
        if pushable:
            logging.info('server pushable')
            taskUrl='/task/server/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='serverTransactionProcess', params={
                                                                                    "key_id": server.key.id()
                                                                                }, countdown=2)

        ## moving this to the top...
        ## WE're getting occasional purchases that result in negative balance.
        ## only permit purcases if the user is pushable.
        #pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        #if pushable:
        #    logging.info('user pushable')
        taskUrl='/task/user/transaction/process'
        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": authorized_user.key.id()
                                                                            }, countdown=2)


        ## uetopia rake transaction is marked processed - just keeping track of it
        description = "Purchase Percentage from: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = uetopia_rake,
            description = description,
            serverKeyId = server.key.id(),
            serverTitle = server.title,
            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,
            userKeyId = authorized_user.key.id(),
            transactionType = "uetopia",
            transactionClass = "purchase rake",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = True,
            materialIcon = MATERIAL_ICON_ADMISSION_FEE,
            materialDisplayClass = "md-primary"
        )




        return self.render_json_response(
            authorization = True,
            success=True,
            ## TODO we're going to need some more info in here, so we can properly respond to this
            ## maybe some sort of string var or two to help identify what should happen in-game
            amount = amountInt,
            userKeyId = userid,
            description = jsonobject['description'],
            itemName = jsonobject['itemName']
        )
