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
from protorpc import remote
from google.appengine.api import taskqueue

from oauth2client.client import GoogleCredentials
import requests
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection


##from apps.uetopia.providers import firebase_helper

import braintree

## not actually using this
## using the rest api instead
## from bitpay.bitpay_client import Client as BitPayClient

from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.orders import OrdersController
from apps.uetopia.controllers.currency import CurrencyController

from apps.uetopia.models.transactions import *

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="transactions", version="v1", description="Transactions API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class TransactionsApi(remote.Service):
    @endpoints.method(TRANSACTION_RESOURCE, TransactionResponse, path='serverDonate', http_method='POST', name='server.donate')
    def serverDonate(self, request):
        """ Donate to a server - PROTECTED """
        logging.info("serverDonate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TransactionResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TransactionResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TransactionResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return TransactionResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        serversController = ServersController()
        lockController = TransactionLockController()

        serverKeyId = request.key_id
        server = serversController.get_by_key_id(serverKeyId)
        if not server:
            return TransactionResponse(response_message='Error: No Server Found. ', response_successful=False)

        amountInt = request.amountInt
        if amountInt < 1:
            return TransactionResponse(response_message='Error: Minimum donation is 1. ', response_successful=False)

        if authorized_user.currencyBalance < amountInt:
            return TransactionResponse(response_message="Error: You don't have enough balance. ", response_successful=False)

        ## TODO more sanity checks

        ## calculate the uetopia rake
        uetopia_rake = int(amountInt * UETOPIA_GROSS_PERCENTAGE_RAKE)
        logging.info("uetopia_rake: %s" % uetopia_rake)

        remaining_donation_to_server = amountInt - uetopia_rake
        logging.info("remaining_donation_to_server: %s" % remaining_donation_to_server)

        transactionController = TransactionsController()

        ## we need two transactions to add to the queue.
        ## One for the server
        description = "Donation from: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = remaining_donation_to_server,
            amountIntGross = amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            ##userKeyId = authorized_user.key.id(),
            ##firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            serverKeyId = server.key.id(),
            serverTitle = server.title,

            ##  transactions are batched and processed all at once.
            transactionType = "server",
            transactionClass = "donation",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-primary"
        )
        ## One for the player
        description = "Donation to: %s" %server.title
        transactionController.create(
            amountInt = -amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            userKeyId = authorized_user.key.id(),
            firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            ##serverKeyId = server.key.id(),
            ##serverTitle = server.title()
            ##  transactions are batched and processed all at once.
            transactionType = "user",
            transactionClass = "donation",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
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

        ## Transaction for uetopia rake - this is marked as processed - just recording it.
        ## only do this if the value is more than zero
        if uetopia_rake > 0:
            description = "Server Donation Percentage from: %s" %authorized_user.title
            recipient_transaction = transactionController.create(
                amountInt = uetopia_rake,
                description = description,
                #serverKeyId = server.key.id(),
                #serverTitle = server.title,
                gameKeyId = server.gameKeyId,
                gameTitle = server.gameTitle,
                serverKeyId = server.key.id(),
                serverTitle = server.title,
                transactionType = "uetopia",
                transactionClass = "game donation rake",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = True,
                materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                materialDisplayClass = "md-primary"
            )

        response = TransactionResponse(
            response_successful = True,
            response_message = "Success.  Donation posted."
        )

        return response

    @endpoints.method(TRANSACTION_RESOURCE, TransactionResponse, path='gameDonate', http_method='POST', name='game.donate')
    def gameDonate(self, request):
        """ Donate to a game - PROTECTED """
        logging.info("gameDonate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TransactionResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TransactionResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TransactionResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return TransactionResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        gamesController = GamesController()
        lockController = TransactionLockController()

        gameKeyId = request.key_id
        game = gamesController.get_by_key_id(gameKeyId)
        if not game:
            return TransactionResponse(response_message='Error: No game Found. ', response_successful=False)

        amountInt = request.amountInt
        if amountInt < 1:
            return TransactionResponse(response_message='Error: Minimum donation is 1. ', response_successful=False)

        if authorized_user.currencyBalance < amountInt:
            return TransactionResponse(response_message="Error: You don't have enough balance. ", response_successful=False)

        ## TODO more sanity checks

        ## calculate the uetopia rake
        uetopia_rake = int(amountInt * UETOPIA_GROSS_PERCENTAGE_RAKE)
        logging.info("uetopia_rake: %s" % uetopia_rake)

        remaining_donation_to_game = amountInt - uetopia_rake
        logging.info("remaining_donation_to_game: %s" % remaining_donation_to_game)

        transactionController = TransactionsController()

        ## we need two transactions to add to the queue.
        ## One for the game
        description = "Donation from: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = remaining_donation_to_game,
            amountIntGross = amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            ##userKeyId = authorized_user.key.id(),
            ##firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            gameKeyId = game.key.id(),
            gameTitle = game.title,

            ##  transactions are batched and processed all at once.
            transactionType = "game",
            transactionClass = "donation",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-primary"
        )
        ## One for the player
        description = "Donation to: %s" %game.title
        transactionController.create(
            amountInt = -amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            userKeyId = authorized_user.key.id(),
            firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            ##serverKeyId = server.key.id(),
            ##serverTitle = server.title()
            ##  transactions are batched and processed all at once.
            transactionType = "user",
            transactionClass = "donation",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-accent"
        )

        ## then start tasks to process them

        ## only start pushable tasks.  If they are not pushable, there is already a task running.
        pushable = lockController.pushable("game:%s"%game.key.id())
        if pushable:
            logging.info('game pushable')
            taskUrl='/task/game/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                    "key_id": game.key.id()
                                                                                }, countdown=2)

        pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": authorized_user.key.id()
                                                                            }, countdown=2)

        ## Transaction for uetopia rake - this is marked as processed - just recording it.
        ## only do this if the value is more than zero
        if uetopia_rake > 0:
            description = "Game Donation Percentage from: %s" %authorized_user.title
            recipient_transaction = transactionController.create(
                amountInt = uetopia_rake,
                description = description,
                #serverKeyId = server.key.id(),
                #serverTitle = server.title,
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                transactionType = "uetopia",
                transactionClass = "game donation rake",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = True,
                materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                materialDisplayClass = "md-primary"
            )

        response = TransactionResponse(
            response_successful = True,
            response_message = "Success.  Donation posted."
        )

        return response

    @endpoints.method(TRANSACTION_RESOURCE, TransactionResponse, path='groupDonate', http_method='POST', name='group.donate')
    def groupDonate(self, request):
        """ Donate to a group - PROTECTED """
        logging.info("groupDonate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TransactionResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TransactionResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TransactionResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return TransactionResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        groupsController = GroupsController()
        lockController = TransactionLockController()

        groupKeyId = request.key_id
        group = groupsController.get_by_key_id(groupKeyId)
        if not group:
            return TransactionResponse(response_message='Error: No group Found. ', response_successful=False)

        amountInt = request.amountInt
        if amountInt < 1:
            return TransactionResponse(response_message='Error: Minimum donation is 1. ', response_successful=False)

        if authorized_user.currencyBalance < amountInt:
            return TransactionResponse(response_message="Error: You don't have enough balance. ", response_successful=False)

        ## TODO more sanity checks

        ## calculate the uetopia rake
        #uetopia_rake = int(amountInt * UETOPIA_GROSS_PERCENTAGE_RAKE)
        #logging.info("uetopia_rake: %s" % uetopia_rake)

        remaining_donation_to_group = amountInt #- uetopia_rake
        logging.info("remaining_donation_to_group: %s" % remaining_donation_to_group)

        transactionController = TransactionsController()

        ## we need two transactions to add to the queue.
        ## One for the group
        description = "Donation from: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = remaining_donation_to_group,
            amountIntGross = amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            ##userKeyId = authorized_user.key.id(),
            ##firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            groupKeyId = group.key.id(),
            groupTitle = group.title,

            ##  transactions are batched and processed all at once.
            transactionType = "group",
            transactionClass = "donation",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-primary"
        )
        ## One for the player
        description = "Donation to: %s" %group.title
        transactionController.create(
            amountInt = -amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            userKeyId = authorized_user.key.id(),
            firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            ##serverKeyId = server.key.id(),
            ##serverTitle = server.title()
            ##  transactions are batched and processed all at once.
            transactionType = "user",
            transactionClass = "donation",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-accent"
        )

        ## then start tasks to process them

        ## only start pushable tasks.  If they are not pushable, there is already a task running.
        pushable = lockController.pushable("group:%s"%group.key.id())
        if pushable:
            logging.info('group pushable')
            taskUrl='/task/group/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                    "key_id": group.key.id()
                                                                                }, countdown=2)

        pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": authorized_user.key.id()
                                                                            }, countdown=2)

        ## Transaction for uetopia rake - this is marked as processed - just recording it.
        ## only do this if the value is more than zero
        #if uetopia_rake > 0:
        #    description = "Game Donation Percentage from: %s" %authorized_user.title
        #    recipient_transaction = transactionController.create(
        #        amountInt = uetopia_rake,
        #        description = description,
        #        #serverKeyId = server.key.id(),
        #        #serverTitle = server.title,
        #        gameKeyId = game.key.id(),
        #        gameTitle = game.title,
        #        transactionType = "uetopia",
        #        transactionClass = "game donation rake",
        #        transactionSender = False,
        #        transactionRecipient = True,
        #        submitted = True,
        #        processed = True,
        #        materialIcon = MATERIAL_ICON_ADMISSION_FEE,
        #        materialDisplayClass = "md-primary"
        #    )

        response = TransactionResponse(
            response_successful = True,
            response_message = "Success.  Donation posted."
        )

        return response

    @endpoints.method(TRANSACTION_COLLECTION_PAGE_RESOURCE, TransactionCollection, path='transactionCollectionGetPage', http_method='POST', name='collection.get.page')
    def transactionCollectionGetPage(self, request):
        """ Get a collection of transactions """
        logging.info("transactionCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TransactionCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TransactionCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TransactionCollection(response_message='Error: No User Record Found. ', response_successful=False)

        serversController = ServersController()
        transactionController = TransactionsController()
        spController = ServerPlayersController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        sort_order = request.sort_order
        direction = request.direction
        transactionType = request.transactionType
        cursor = request.cursor
        more = False

        entities = []

        if request.serverKeyId:
            logging.info('serverKeyId found')
            server = serversController.get_by_key_id(int(request.serverKeyId))
            if not server:
                logging.info('server not found')
                return TransactionCollection(response_message='Error: No Server Record Found. ', response_successful=False)

            if transactionType == 'server':
                logging.info('transactionType:  server')
                if server.userKeyId == authorized_user.key.id():
                    logging.info('developer user match')
                    ## this is a developer request.  Send all of the server's transactions
                    entities, cursor, more = transactionController.list_page_by_serverKeyId(int(request.serverKeyId), start_cursor=curs)
            elif transactionType == 'serverplayer':
                logging.info('transactionType:  serverplayer')
                ## this is a regular user.  Send all serverplayer transactions
                server_player = spController.get_server_user(server.key.id(), authorized_user.key.id())
                if server_player:
                    entities, cursor, more = transactionController.list_page_by_serverPlayerKeyId(server_player.key.id(), start_cursor=curs)
        elif request.gameKeyId:
            logging.info('gameKeyId found')
            if transactionType == 'game':
                entities, cursor, more = transactionController.list_page_by_gameKeyId(int(request.gameKeyId), start_cursor=curs)
        elif request.groupKeyId:
            logging.info('groupKeyId found')
            if transactionType == 'group':
                ## make sure the user has permission first.
                ## check if the authenticated user is already a member
                group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

                if not group_member:
                    return TransactionCollection(response_message='Error: Not a member of this group.', response_successful=False)

                # get the role
                group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
                if not group_member_role:
                    return TransactionCollection(response_message='Error: Role not found.', response_successful=False)

                if not group_member_role.view_transactions:
                    return TransactionCollection(response_message='Error: You do not have sufficient permissions to view transactions for this group.', response_successful=False)

                entities, cursor, more = transactionController.list_page_by_groupKeyId(int(request.groupKeyId), start_cursor=curs)
        else:
            entities, cursor, more = transactionController.list_page_by_userKeyId(authorized_user.key.id(), start_cursor=curs)

        entity_list = []

        for entity in entities:
            entity_list.append(TransactionResponse(
                key_id = entity.key.id(),
                description = entity.description,
                amountInt = entity.amountInt,
                newBalanceInt = entity.newBalanceInt,
                transactionType = entity.transactionType,
                transactionClass = entity.transactionClass,
                materialIcon = entity.materialIcon,
                materialDisplayClass = entity.materialDisplayClass,
                created = entity.created.isoformat()
            ))

        if cursor:
            cursor_urlsafe = cursor.urlsafe()
        else:
            cursor_urlsafe = None

        response = TransactionCollection(
            transactions = entity_list,
            more = more,
            cursor = cursor_urlsafe,
            response_successful = True,
            response_message = "Success.  Returning transaction list."
        )

        return response

    @endpoints.method(TRANSACTION_RESOURCE, TransactionResponse, path='userTip', http_method='POST', name='user.tip')
    def userTip(self, request):
        """ Tip a user - PROTECTED """
        logging.info("userTip")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TransactionResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TransactionResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        userController = UsersController()
        authorized_user = userController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TransactionResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return TransactionResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        #serversController = ServersController()
        lockController = TransactionLockController()
        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        transactionController = TransactionsController()


        amountInt = request.amountInt
        if amountInt < 1:
            return TransactionResponse(response_message='Error: Minimum donation is 1. ', response_successful=False)

        ## check to see if thie is a Group > user transaction
        if request.fromGroup:
            logging.info('detected a group to user transaction')
            if request.fromGroupKeyId:
                logging.info('found a groupKeyId in the request')
                group = groupsController.get_by_key_id(request.fromGroupKeyId)
                if not group:
                    logging.info('the group could not be found with the specified key')
                    return TransactionResponse(response_message='Error: the group could not be found with the specified key. ', response_successful=False)


                requesting_group_member = groupUsersController.get_by_groupKeyId_userKeyId(group.key.id(), authorized_user.key.id())
                if not requesting_group_member:
                    logging.info('could not find your group member record')
                    return TransactionResponse(response_message='Error: could not find your group member record. ', response_successful=False)


                if not requesting_group_member.roleKeyId:
                    logging.info('could not find your group member role')
                    return TransactionResponse(response_message='Error: could not find your group member role. ', response_successful=False)

                requesting_group_member_role = groupRolesController.get_by_key_id(requesting_group_member.roleKeyId)
                if not requesting_group_member_role:
                    logging.info('could not find your group member role')
                    return TransactionResponse(response_message='Error: could not find your group member role. ', response_successful=False)

                if not requesting_group_member_role.donate_to_members:
                    logging.info('You do not have permission to donate to users')
                    return TransactionResponse(response_message='Error: You do not have permission to donate to users. ', response_successful=False)

                ## coming from the group user page this is a group_userKey
                targetUserKeyId = int(request.key_id)
                logging.info(targetUserKeyId)

                ## make sure the target user is a member of this group
                target_group_member = groupUsersController.get_by_key_id(targetUserKeyId)
                if not target_group_member:
                    logging.info('target group member not found')
                    return TransactionResponse(response_message='Error: target group member not found. ', response_successful=False)

                if target_group_member.groupKeyId != group.key.id():
                    logging.info('group member and group mismatch')
                    return TransactionResponse(response_message='Error: group member and group mismatch. ', response_successful=False)

                targetUser = userController.get_by_key_id(target_group_member.userKeyId)
                if not targetUser:
                    return TransactionResponse(response_message='Error: No User Found. ', response_successful=False)



                ## check group balance
                if group.currencyBalance < amountInt:
                    logging.info("Error: The group does not have enough balance. ")
                    return TransactionResponse(response_message="Error: The group does not have enough balance. ", response_successful=False)

                ## we need two transactions to add to the queue.
                ## One for the recipient
                description = "Group donation from: %s" %group.title
                recipient_transaction = transactionController.create(
                    amountInt = amountInt,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    userKeyId = targetUser.key.id(),
                    firebaseUser = targetUser.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    ##serverKeyId = server.key.id(),
                    ##serverTitle = server.title,

                    ##  transactions are batched and processed all at once.
                    transactionType = "user",
                    transactionClass = "group_donation",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_TIP,
                    materialDisplayClass = "md-primary"
                )
                ## One for the player
                description = "Donation to: %s" %targetUser.title
                transactionController.create(
                    amountInt = -amountInt,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    ##userKeyId = authorized_user.key.id(),
                    ##firebaseUser = authorized_user.firebaseUser,
                    groupKeyId = group.key.id(),
                    groupTitle = group.title,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    ##serverKeyId = server.key.id(),
                    ##serverTitle = server.title()
                    ##  transactions are batched and processed all at once.
                    transactionType = "group",
                    transactionClass = "user_donation",
                    transactionSender = True,
                    transactionRecipient = False,
                    recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_TIP,
                    materialDisplayClass = "md-accent"
                )

                ## then start tasks to process them

                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                pushable = lockController.pushable("user:%s"%targetUser.key.id())
                if pushable:
                    logging.info('targetUser pushable')
                    taskUrl='/task/user/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                            "key_id": targetUser.key.id()
                                                                                        }, countdown=2)

                pushable = lockController.pushable("group:%s"%group.key.id())
                if pushable:
                    logging.info('group pushable')
                    taskUrl='/task/group/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                        "key_id": group.key.id()
                                                                                    }, countdown=2)

                response = TransactionResponse(
                    response_successful = True,
                    response_message = "Success.  User Donation posted."
                )

                return response




        targetUserKeyId = int(request.key_id)
        logging.info(targetUserKeyId)
        targetUser = userController.get_by_key_id(targetUserKeyId)
        if not targetUser:
            return TransactionResponse(response_message='Error: No User Found. ', response_successful=False)

        if authorized_user.currencyBalance < amountInt:
            return TransactionResponse(response_message="Error: You don't have enough balance. ", response_successful=False)

        ## TODO more sanity checks

        ## TODO Only run this if the sender is pushable.



        ## we need two transactions to add to the queue.
        ## One for the recipient
        description = "Tip from: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            userKeyId = targetUser.key.id(),
            firebaseUser = targetUser.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            ##serverKeyId = server.key.id(),
            ##serverTitle = server.title,

            ##  transactions are batched and processed all at once.
            transactionType = "user",
            transactionClass = "tip",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_TIP,
            materialDisplayClass = "md-primary"
        )
        ## One for the player
        description = "Tip to: %s" %targetUser.title
        transactionController.create(
            amountInt = -amountInt,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            userKeyId = authorized_user.key.id(),
            firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            ##serverKeyId = server.key.id(),
            ##serverTitle = server.title()
            ##  transactions are batched and processed all at once.
            transactionType = "user",
            transactionClass = "tip",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_TIP,
            materialDisplayClass = "md-accent"
        )

        ## then start tasks to process them

        ## only start pushable tasks.  If they are not pushable, there is already a task running.
        pushable = lockController.pushable("user:%s"%targetUser.key.id())
        if pushable:
            logging.info('targetUser pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": targetUser.key.id()
                                                                                }, countdown=2)

        pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": authorized_user.key.id()
                                                                            }, countdown=2)

        response = TransactionResponse(
            response_successful = True,
            response_message = "Success.  Tip posted."
        )

        return response

    @endpoints.method(BITPAY_INVOICE_RESOURCE, BitPayInvoiceResponse, path='createBitpayInvoice', http_method='POST', name='bitpay.invoice.create')
    def createBitpayInvoice(self, request):
        """ Create a bitpay invoice - PROTECTED """
        logging.info("createBitpayInvoice")

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return BitPayInvoiceResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return BitPayInvoiceResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return BitPayInvoiceResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        userController = UsersController()
        orderController = OrdersController()
        cController = CurrencyController()

        authorized_user = userController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return BitPayInvoiceResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        """
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return BitPayInvoiceResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)
        """
        value_in_btc = request.amountBTC

        if value_in_btc < .00040000:
            logging.info('Requested cred purchase amount too low.')
            return BitPayInvoiceResponse(response_message='Error: The minimum purchase amount is 40,000 CRED', response_successful=False)

        if value_in_btc > .01000000:
            logging.info('Requested cred purchase amount too high.')
            return BitPayInvoiceResponse(response_message='Error: The maximum purchase amount is 1,000,000 CRED', response_successful=False)

        value_in_cred = value_in_btc * 100000000

        ## calculate out the value in USD
        btc_currency = cController.get_by_iso_code('BTC')

        value_in_usd = float(value_in_cred) * float(btc_currency.value_to_usd)

        ## Create an order database record
        order = orderController.create(
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            firebaseUser = authorized_user.firebaseUser,
            processor = "bitpay",
            value_in_cred = int(value_in_cred),
            value_in_usd = value_in_usd,
            status_paid = False,
            status_confirmed = False,
        )


        ## https://support.bitpay.com/hc/en-us/articles/115003001203-How-do-I-configure-and-use-the-BitPay-Python-Library-
        ## https://bitpay.com/docs/invoice-callbacks

        ## this is not working
        """
        bp_client = BitPayClient(api_uri="https://bitpay.com") #if api_uri is not passed, it defaults to "https://bitpay.com"
        bp_client.pair_pos_client(BITPAY_PAIRING_CODE)

        #bp_client = BitPayClient(api_uri="https://test.bitpay.com")
        #bp_client.create_token("merchant")

        notificationURL = "https://ue4topia.appspot.com/bitpay/invoice/callback"

        invoice = bp_client.create_invoice({"price": value_in_usd,
                                "currency": "USD",
                                "transactionSpeed":"medium",
                                "fullNotifications":"true",
                                "notificationURL": notificationURL,
                                "buyer":{str(authorized_user.email)},
                                "orderId":str(order.key.id()),
                                "token": bp_client.tokens['pos']})

        logging.info(invoice)
        """

        ## Guessing that we are supposed to use the API endpoint instead...
        ## documentation is fucking aweful and confusing

        ## https://bitpay.com/downloads/bitpayApi.pdf



        url = "https://bitpay.com/api/invoice"

        #value_in_btc = value_in_cred / 100000000.0
        logging.info("value_in_btc: %s"% value_in_btc)

        #credentials = GoogleCredentials.get_application_default()
        #http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        payload = {
                  "price": value_in_btc,
                  "currency": "BTC",
                  "posData": str(order.key.id()),
                  "notificationURL": BITPAY_NOTIFICATION_URL,
                  "buyerEmail": authorized_user.email
                  }

        response = requests.post(url, json=payload, auth=(BITPAY_API_KEY_ID, ''))

        logging.info(response.status_code)
        response_json = response.json()
        logging.info(response_json)
        logging.info(response_json['url'])

        # Hash the params string to produce the Sign header value
        #H = hmac.new(shared_secret, digestmod=hashlib.sha512)
        #H.update(params)
        #sign = H.hexdigest()


        return BitPayInvoiceResponse(response_message='Success', response_successful=True, bitpayurl=response_json['url'])

    @endpoints.method(BRAINTREE_TOKEN_RESOURCE, BraintreeTokenResponse, path='createBraintreeToken', http_method='POST', name='braintree.token.create')
    def createBraintreeToken(self, request):
        """ Create a braintree token - PROTECTED """
        logging.info("createBraintreeToken")

        ## ONLY allow this from authorized domains
        #request_origin = self.request_state.headers['origin']
        #logging.info("request_origin: %s" %request_origin)
        #if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
        #    logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
        #    return BraintreeTokenResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Production,
                #braintree.Environment.Sandbox,
                merchant_id=BRAINTREE_MERCHANT_ID,
                public_key=BRAINTREE_PUBLIC_KEY,
                private_key=BRAINTREE_PRIVATE_KEY
            )
        )

        response = BraintreeTokenResponse(
            token = gateway.client_token.generate(),
            response_message = 'Success',
            response_successful = True
        )
        logging.info('response')

        return response

    @endpoints.method(BRAINTREE_TOKEN_RESOURCE, BraintreeTokenResponse, path='createBraintreeTransaction', http_method='POST', name='braintree.transaction.create')
    def createBraintreeTransaction(self, request):
        """ Create a braintree transaction - PROTECTED """
        logging.info("createBraintreeTransaction")

        ## ONLY allow this from authorized domains
        #request_origin = self.request_state.headers['origin']
        #logging.info("request_origin: %s" %request_origin)
        #if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
        #    logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
        #    return BraintreeTokenResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return BraintreeTokenResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return BraintreeTokenResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)


        userController = UsersController()
        orderController = OrdersController()
        cController = CurrencyController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()

        authorized_user = userController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return BraintreeTokenResponse(response_message='Error: No User Record Found. ', response_successful=False)

        payment_method_nonce = request.payment_method_nonce;
        amountUSD = request.amountUSD;
        logging.info("amountUSD: %s" %amountUSD)
        #amountUSDFloat = float(amountUSD)

        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Production,
                #braintree.Environment.Sandbox,
                merchant_id=BRAINTREE_MERCHANT_ID,
                public_key=BRAINTREE_PUBLIC_KEY,
                private_key=BRAINTREE_PRIVATE_KEY
            )
        )

        result = gateway.transaction.sale({
            "amount": str(amountUSD),
            "payment_method_nonce": payment_method_nonce,
            "options": {
              "submit_for_settlement": True
            }
        })

        logging.info(result)

        if result.is_success:
            logging.info('Success')
            transaction = result.transaction
            logging.info(transaction)

            ## At this stage we should have a valid transaction

            btc_currency = cController.get_by_iso_code('BTC')

            usd_amount_from_braintree = float(result.transaction.amount) ## use this over the amount in the post
            logging.info('usd_amount_from_braintree: %s' %usd_amount_from_braintree)

            #value_in_usd = float(value_in_cred) * float(btc_currency.value_to_usd)

            ## this is confusing, because we've already done calculations on this 'value_to_usd' value, so it is different than the calculation in the JS
            ## so we'll redo these calculations again
            one_hundred_million_cred_equals = 1.0 / btc_currency.value_to_usd #9256.19460179101
            one_cred_equals = '%f' % (one_hundred_million_cred_equals/100000000.)  #'0.000093'
            one_cred_equals_float = float(one_cred_equals) # 0.000093

            # 5.00 * 0.000112137594 * 100000000 = 56068.797
            value_in_cred = usd_amount_from_braintree / one_cred_equals_float
            logging.info('value_in_cred: %s' %value_in_cred)

            # it's still not the exact same value we get in JS all of the time.  Might need to specify rounding funcitons.

            ## Create an order database record
            order = orderController.create(
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                firebaseUser = authorized_user.firebaseUser,
                processor = "brantree",
                value_in_cred = int(value_in_cred),
                value_in_usd = usd_amount_from_braintree,
                status_paid = True,
                status_confirmed = True,
            )


            description = "%s CRED purchased for $%.2f" %(int(value_in_cred), usd_amount_from_braintree)

            ## create the cred transaction
            recipient_transaction = transactionController.create(
                amountInt = int(value_in_cred),
                ##amount = ndb.FloatProperty(indexed=False) # for display
                ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                ##newBalance = ndb.FloatProperty(indexed=False) # for display
                description = description,
                userKeyId = authorized_user.key.id(),
                firebaseUser = authorized_user.firebaseUser,
                ##targetUserKeyId = ndb.IntegerProperty()
                ##serverKeyId = server.key.id(),
                ##serverTitle = server.title,

                ##  transactions are batched and processed all at once.
                transactionType = "user",
                transactionClass = "Braintree Purchase",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_CRED_PURCHASE,
                materialDisplayClass = "md-primary"
            )

            pushable = lockController.pushable("user:%s"%authorized_user.key.id())
            if pushable:
                logging.info('user pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": authorized_user.key.id()
                                                                                }, countdown=2)

            ## create an alert

            ## push to admin discord webhook
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "%s | %s CRED | $%s" % (authorized_user.email, int(value_in_cred), amountUSD)
            discord_data = { "embeds": [{"title": "Cred Purchase", "url": "https://example.com", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(DISCORD_WEBHOOK_PAYMENTS,
                              "POST",
                              data,
                              headers=headers)



            response = BraintreeTokenResponse(
                response_message = 'Success',
                response_successful = True
            )

            return response
        else:
            response = BraintreeTokenResponse(
                response_message = str(result),
                response_successful = False
            )

            return response
