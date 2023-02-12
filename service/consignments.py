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

##from apps.uetopia.providers import firebase_helper

## endpoints v2 wants a "collection" so it can build the openapi files
#from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.models.store_item_consignments import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.groups import GroupsController

from apps.uetopia.controllers.store_item_consignments import StoreItemConsignmentsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="consignments", version="v1", description="Consignments API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class ConsignmentsApi(remote.Service):
    @endpoints.method(STORE_ITEM_CON_CREATE_RESOURCE, StoreItemConsignmentResponse, path='create', http_method='POST', name='create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def create(self, request):
        """ Create a consignment - PROTECTED """
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return StoreItemConsignmentResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return StoreItemConsignmentResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        userController = UsersController()

        authorized_user = userController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return StoreItemConsignmentResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return StoreItemConsignmentResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        storeItemConsignmentController = StoreItemConsignmentsController()
        groupController = GroupsController()

        if request.pricePerUnit < 0:
            logging.info('pricePerUnit cannot be negative')
            return StoreItemConsignmentResponse(response_message='Error: pricePerUnit cannot be negative.', response_successful=False)

        ## get the game
        game = gController.get_by_key_id(int(request.gameKeyId))
        if not game:
            logging.info('Game not found.')
            return StoreItemConsignmentResponse(response_message='Error: Game not found.', response_successful=False)

        # make sure this user is the game owner
        if game.userKeyId != authorized_user.key.id():
            logging.info('User is not game owner.')
            return StoreItemConsignmentResponse(response_message='Error: User is not game owner.', response_successful=False)

        # get/check the supplied userKeyId or groupKeyId
        if request.group:
            logging.info('this is a group consignment')
            if not request.groupKeyId:
                logging.info('groupKeyId not found.')
                return StoreItemConsignmentResponse(response_message='Error: The groupKeyId was not found.', response_successful=False)

            logging.info('got groupKeyId')
            group = groupController.get_by_key_id(int(request.groupKeyId))
            if not group:
                logging.info('group not found.')
                return StoreItemConsignmentResponse(response_message='Error: The group was not found.', response_successful=False)

            consignment = storeItemConsignmentController.create(
                title = request.title,
                description = request.description,
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                group = request.group,
                groupKeyId = group.key.id(),
                groupTitle = group.title,
                pricePerUnit = request.pricePerUnit,
                )

            ## DIscord message to the group if configured
            if group.discord_webhook and group.discord_subscribe_consignments:
                link = "https://ue4topia.appspot.com/#/game/%s" % (game.key.id())
                message = "%s %s %s" %(request.pricePerUnit, request.title, link)
                http_auth = Http()
                headers = {"Content-Type": "application/json"}

                discord_data = { "embeds": [{"title": "New Consignment Set Up", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(group.discord_webhook,
                                  "POST",
                                  data,
                                  headers=headers)


        else:
            logging.info('this is a user consignment')

            if not request.userKeyId:
                logging.info('userKeyId not found.')
                return StoreItemConsignmentResponse(response_message='Error: The userKeyId was not found.', response_successful=False)

            logging.info('got userKeyId')
            consignment_user = userController.get_by_key_id(int(request.userKeyId))
            if not consignment_user:
                logging.info('consignment_user not found.')
                return StoreItemConsignmentResponse(response_message='Error: The consignment_user was not found.', response_successful=False)

            consignment = storeItemConsignmentController.create(
                title = request.title,
                description = request.description,
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                userKeyId = consignment_user.key.id(),
                userTitle = consignment_user.title,
                group = request.group,
                pricePerUnit = request.pricePerUnit,
                )

            ## DIscord message to the user if configured
            if consignment_user.discord_webhook and consignment_user.discord_subscribe_consignments:
                link = "https://ue4topia.appspot.com/#/game/%s" % (game.key.id())
                message = "%s %s %s" %(request.pricePerUnit, request.title, link)
                http_auth = Http()
                headers = {"Content-Type": "application/json"}

                discord_data = { "embeds": [{"title": "New Consignment Set Up", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(consignment_user.discord_webhook,
                                  "POST",
                                  data,
                                  headers=headers)


        # send out a discord alert to the game owner.
        # no bool for this since it should not really be optional
        if game.discord_webhook_admin:
            link = "https://ue4topia.appspot.com/#/game/%s" % (game.key.id())
            message = "New consignment submitted.  %s" %link
            http_auth = Http()
            headers = {"Content-Type": "application/json"}

            discord_data = { "embeds": [{"title": "New Consignment", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)




        ## update firebase
        #taskUrl='/task/game/firebase/update'
        #taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game.key.id()}, countdown = 2,)


        return StoreItemConsignmentResponse(response_message="Offer Created", response_successful=True)


    @endpoints.method(STORE_ITEM_CON_COLLECTION_PAGE_RESOURCE, StoreItemConsignmentCollection, path='collectionGetPage', http_method='POST', name='collection.get.page')
    def collectionGetPage(self, request):
        """ Get a collection of Consignments """
        logging.info("collectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return StoreItemConsignmentCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return StoreItemConsignmentCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return StoreItemConsignmentCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        storeItemConsignmentController = StoreItemConsignmentsController()


        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        #sort_order = request.sort_order
        #direction = request.direction

        consignments = []

        ## if gameModeKeyId is supplied, get the ads for the game.  Verify game owner
        if request.gameKeyId:
            logging.info('gameKeyId found')

            game = gController.get_by_key_id(request.gameKeyId)
            if not game:
                logging.info('Game not found.')
                return StoreItemConsignmentCollection(response_message='Error: Game not found.', response_successful=False)

            if game.userKeyId != authorized_user.key.id():
                logging.info('Only the game owner can view consignments')
                return StoreItemConsignmentCollection(response_message='Error: Only the game owner can view consignments.', response_successful=False)

            consignments = storeItemConsignmentController.get_by_gameKeyId(game.key.id())

        entity_list = []
        for consignment in consignments:
            entity_list.append(StoreItemConsignmentResponse(
                key_id = consignment.key.id(),
                created= consignment.created.isoformat(' '),
                title = consignment.title,
                description = consignment.description,
                gameKeyId = consignment.gameKeyId,
                gameTitle = consignment.gameTitle,
                userKeyId = consignment.userKeyId,
                userTitle = consignment.userTitle,
                group = consignment.group,
                groupKeyId = consignment.groupKeyId,
                groupTitle = consignment.groupTitle,
                pricePerUnit = consignment.pricePerUnit
            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = StoreItemConsignmentCollection(
            store_item_cons = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(STORE_ITEM_CON_GET_RESOURCE, StoreItemConsignmentResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a consignment """
        logging.info("consignment get")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return StoreItemConsignmentResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return StoreItemConsignmentResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return StoreItemConsignmentResponse(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        storeItemConsignmentController = StoreItemConsignmentsController()



        ## TODO allow the recipient to view it?

        ## if a voucherKey was supplied, use that to look up the connected offer
        if not request.key_id:
            logging.info('did not find key_id')
            return StoreItemConsignmentResponse(response_message='Error: key_id is required.', response_successful=False)


        consignment = storeItemConsignmentController.get_by_key_id(int(request.key_id))
        if not consignment:
            logging.info('consignment not found')
            return StoreItemConsignmentResponse(response_message='Error: No consignment Record Found. ', response_successful=False)

        game = gController.get_by_key_id(consignment.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return StoreItemConsignmentResponse(response_message='Error: Game not found.', response_successful=False)

        if game.userKeyId != authorized_user.key.id():
            logging.info('Only the game owner can view consignments')
            return StoreItemConsignmentResponse(response_message='Error: Only the game owner can view consignments.', response_successful=False)


        return StoreItemConsignmentResponse(
            key_id = consignment.key.id(),
            title = consignment.title,
            description = consignment.description,
            gameKeyId = consignment.gameKeyId,
            gameTitle = consignment.gameTitle,
            userKeyId = consignment.userKeyId,
            userTitle = consignment.userTitle,
            group = consignment.group,
            groupKeyId = consignment.groupKeyId,
            groupTitle = consignment.groupTitle,
            pricePerUnit = consignment.pricePerUnit,
            response_message='Found consignment',
            response_successful=True
        )




    @endpoints.method(STORE_ITEM_CON_EDIT_RESOURCE, StoreItemConsignmentResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update an consignment """
        logging.info("consignment")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return StoreItemConsignmentResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return StoreItemConsignmentResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        userController = UsersController()

        authorized_user = userController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return StoreItemConsignmentResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return StoreItemConsignmentResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        storeItemConsignmentController = StoreItemConsignmentsController()
        groupController = GroupsController()

        ## get the requested consignment

        requested_consignment = storeItemConsignmentController.get_by_key_id(request.key_id)

        if not requested_consignment:
            logging.info('requested consignment not found')
            return StoreItemConsignmentResponse(response_message='Error: No consignment Found. ', response_successful=False)

        ## check to see if the user is the owner of the game
        game = gController.get_by_key_id(requested_consignment.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return StoreItemConsignmentResponse(response_message='Error: Game not found.', response_successful=False)

        if game.userKeyId != authorized_user.key.id():
            logging.info('Only the game owner can view offers')
            return StoreItemConsignmentResponse(response_message='Error: Only the game owner can update offers.', response_successful=False)


        requested_consignment.title = request.title
        requested_consignment.description = request.description
        #requested_consignment.gameKeyId = request.gameKeyId
        requested_consignment.pricePerUnit = request.pricePerUnit

        if request.group:
            logging.info('this is a group consignment')

            if not request.groupKeyId:
                logging.info('The groupKeyId was not found.')
                return StoreItemConsignmentResponse(response_message='Error: The groupKeyId was not found.', response_successful=False)

            logging.info('got groupKeyId')

            group = groupController.get_by_key_id(request.groupKeyId)
            if not group:
                logging.info('group not found.')
                return StoreItemConsignmentResponse(response_message='Error: The group was not found.', response_successful=False)

            requested_consignment.group = True
            requested_consignment.groupKeyId = group.key.id()
            requested_consignment.groupTitle = group.title

            ## DIscord message to the group if configured
            if group.discord_webhook and group.discord_subscribe_consignments:
                link = "https://ue4topia.appspot.com/#/game/%s" % (game.key.id())
                message = "%s %s %s" %(request.pricePerUnit, request.title, link)
                http_auth = Http()
                headers = {"Content-Type": "application/json"}

                discord_data = { "embeds": [{"title": "Consignment Updated", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(group.discord_webhook,
                                  "POST",
                                  data,
                                  headers=headers)
        else:
            logging.info('this is a user consignment')

            if not request.userKeyId:
                logging.info('userKeyId not found.')
                return StoreItemConsignmentResponse(response_message='Error: The userKeyId was not found.', response_successful=False)

            logging.info('got userKeyId')
            consignment_user = userController.get_by_key_id(request.userKeyId)
            if not consignment_user:
                logging.info('consignment_user not found.')
                return StoreItemConsignmentResponse(response_message='Error: The consignment_user was not found.', response_successful=False)

            requested_consignment.group = False
            requested_consignment.userKeyId = consignment_user.key.id()
            requested_consignment.userTitle = consignment_user.title

            ## DIscord message to the user if configured
            if consignment_user.discord_webhook and consignment_user.discord_subscribe_consignments:
                link = "https://ue4topia.appspot.com/#/game/%s" % (game.key.id())
                message = "%s %s %s" %(request.pricePerUnit, request.title, link)
                http_auth = Http()
                headers = {"Content-Type": "application/json"}

                discord_data = { "embeds": [{"title": "Consignment Updated", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(consignment_user.discord_webhook,
                                  "POST",
                                  data,
                                  headers=headers)

        storeItemConsignmentController.update(requested_consignment)

        return StoreItemConsignmentResponse(response_message='Success.  Consignment updated.', response_successful=True)
