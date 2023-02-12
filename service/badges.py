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

from apps.uetopia.models.badges import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController

from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.offers import OffersController
from apps.uetopia.controllers.vouchers import VouchersController
from apps.uetopia.controllers.badges import BadgesController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="badges", version="v1", description="Badges API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class BadgesApi(remote.Service):
    @endpoints.method(BADGE_COLLECTION_PAGE_RESOURCE, BadgeCollection, path='badgeCollectionGetPage', http_method='POST', name='collection.get.page')
    def badgeCollectionGetPage(self, request):
        """ Get a collection of badges """
        logging.info("badgeCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return OfferCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return OfferCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return OfferCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        offerController = OffersController()
        badgeController = BadgesController()


        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        #sort_order = request.sort_order
        #direction = request.direction

        badges = badgeController.get_active_by_userKeyId(authorized_user.key.id())

        entity_list = []
        for badge in badges:
            entity_list.append(BadgeResponse(
                key_id = badge.key.id(),
                created= badge.created.isoformat(' '),
                title = badge.title,
                description = badge.description,
                gameKeyId = badge.gameKeyId,
                gameTitle = badge.gameTitle,
                offerKeyId = badge.offerKeyId,
                offerTitle =  badge.offerTitle,
                voucherKeyId = badge.voucherKeyId,
                voucherTitle = badge.voucherTitle,
                offerType = badge.offerType,
                tags = badge.tags,
                icon_url = badge.icon_url,
                active = badge.active,
                autoRefresh = badge.autoRefresh
            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = BadgeCollection(
            badges = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(BADGE_RESOURCE, BadgeResponse, path='badgeGet', http_method='POST', name='get')
    def badgeGet(self, request):
        """ Get a badge """
        logging.info("badgeGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return BadgeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return BadgeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return BadgeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gController = GamesController()
        offerController = OffersController()
        voucherController = VouchersController()
        badgeController = BadgesController()

        logging.info('looking up from key_id')
        badge = badgeController.get_by_key_id(request.key_id)
        if not badge:
            logging.info('badge not found')
            return BadgeResponse(response_message='Error: No Badge Record Found. ', response_successful=False)

        if badge.userKeyId != authorized_user.key.id():
            logging.info('user mismatch')
            return BadgeResponse(response_message='Error: No Badge Record Found. ', response_successful=False)

        return BadgeResponse(
            key_id = badge.key.id(),
            title = badge.title,
            description = badge.description,
            gameKeyId = badge.gameKeyId,
            gameTitle = badge.gameTitle,
            offerKeyId = badge.offerKeyId,
            offerTitle = badge.offerTitle,
            voucherKeyId = badge.voucherKeyId,
            voucherTitle = badge.voucherTitle,
            offerType = badge.offerType,
            tags = badge.tags,
            icon_url = badge.icon_url,
            active = badge.active,
            autoRefresh = badge.autoRefresh,
            response_message='Found available offer',
            response_successful=True
        )


    @endpoints.method(BADGE_RESOURCE, BadgeResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update a badge - PROTECTED """
        logging.info("update")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return BadgeResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return BadgeResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return BadgeResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return BadgeResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        badgeController = BadgesController()
        offerController = OffersController()
        ## get the requested badge

        requested_badge = badgeController.get_by_key_id(request.key_id)

        if not requested_badge:
            logging.info('requested badge not found')
            return BadgeResponse(response_message='Error: No badge Found. ', response_successful=False)

        if requested_badge.userKeyId != authorized_user.key.id():
            logging.info('Only the badge owner can view it')
            return BadgeResponse(response_message='Error: Only the badge owner can update it.', response_successful=False)

        if requested_badge.autoRefresh != request.autoRefresh:
            logging.info('autoRefresh is different')
            requested_badge.autoRefresh = request.autoRefresh

            badgeController.update(requested_badge)

        return BadgeResponse(response_message='Success.  Badge updated.', response_successful=True)
