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
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class serverPlayerRewardHandler(BaseHandler):
    def post(self, userid):
        """
        Reward a server player with CRED
        Requires http headers:  Key, Sign
        Requires JSON parameters:  nonce, amount, description
        """

        serverController = ServersController()
        ucontroller = UsersController()
        spController = ServerPlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()

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
            logging.info("No id_token found.  NOT Doing it the old way - deprecated")

            return self.render_json_response(
                authorization = True,
                success=False,
                ## TODO we're going to need some more info in here, so we can properly respond to this
                ## maybe some sort of string var or two to help identify what should happen in-game
                #amount = amountInt,
                #userKeyId = userid,
                #description = jsonobject['description'],
                #itemName = jsonobject['itemName']
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
                success=False
            )

        if 'description' not in jsonobject:
            logging.info("Found description in json")
            return self.render_json_response(
                authorization = True,
                success=False
            )

        ## make sure the server has enough balance to cover it
        if server.serverCurrency < jsonobject['amount']:
            logging.info('server does not have enough balance to cover it')
            return self.render_json_response(
                authorization = True,
                success=False
            )

        ## TODO any other checks needed?

        logging.info('checks passed')

        ## make transactions, and queue them up
        transactionController = TransactionsController()

        amountInt = jsonobject['amount']

        ## we need two transactions to add to the queue.
        ## One for the user
        #description = "Reward from: %s" %server.title
        description = jsonobject['description']
        recipient_transaction = transactionController.create(
            amountInt = amountInt,
            description = description,
            serverKeyId = server.key.id(),
            serverTitle = server.title,
            userKeyId = authorized_user.key.id(),

            ##  transactions are batched and processed all at once.
            transactionType = "user",
            transactionClass = "reward",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_REWARD,
            materialDisplayClass = "md-primary"
        )
        ## One for the server
        description = "Reward to: %s" %authorized_user.title
        transactionController.create(
            amountInt = -amountInt,
            description = description,
            serverKeyId = server.key.id(),
            serverTitle = server.title,

            transactionType = "server",
            transactionClass = "reward",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_REWARD,
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

        pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": authorized_user.key.id()
                                                                            }, countdown=2)





        logging.info(amountInt)

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
