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

from apps.uetopia.models.ads import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.ads import AdsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="ads", version="v1", description="Ads API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class AdsApi(remote.Service):
    @endpoints.method(AD_RESOURCE, AdResponse, path='create', http_method='POST', name='create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def create(self, request):
        """ Create an ad - PROTECTED """
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return AdResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return AdResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return AdResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return AdResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        gameModeController = GameModesController()
        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        groupGameController = GroupGamesController()
        adController = AdsController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()

        ## get the group
        group = groupsController.get_by_key_id(int(request.groupKeyId))
        if not group:
            logging.info('Group not found')
            return AdResponse(response_message='Error: Group not found.', response_successful=False)

        # get the group game
        group_game = groupGameController.get_by_key_id(int(request.groupGameKeyId))
        if not group_game:
            logging.info('Group Game not found')
            return AdResponse(response_message='Error: Group Game not found.', response_successful=False)

        ## check if the authenticated user is a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group.')
            return AdResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('Role not found')
            return AdResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.create_ads:
            logging.info('You do not have sufficient permissions to create ads for this group.')
            return AdResponse(response_message='Error: You do not have sufficient permissions to create ads for this group.', response_successful=False)

        # get the game via groupgame
        game = gController.get_by_key_id(group_game.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return AdResponse(response_message='Error: Game not found.', response_successful=False)

        # get the game mode
        game_mode = gameModeController.get_by_key_id(request.gameModeKeyId)
        if not game_mode:
            logging.info('Game Mode not found.')
            return AdResponse(response_message='Error: Game Mode not found.', response_successful=False)

        ## check to see if approval is required
        if game_mode.ads_require_approval:
            logging.info("ads require approval")
            approved = False
            active = False

        else:
            approved = True
            active = True

        ## check to see if the bid is high enough
        if request.bid_per_impression < game_mode.ads_minimum_bid_per_impression:
            logging.info('bid too low')
            message = 'Error: Your bid per impression was too low. The minimum for this game mode is %s' %game_mode.ads_minimum_bid_per_impression
            return AdResponse(response_message=message, response_successful=False)

        ## make sure the number of impressions is in range.
        if request.number_of_impressions < 1:
            logging.info('Number of impressions is too low.')
            return AdResponse(response_message='Error: Number of impressions is too low.  The minimum is 1', response_successful=False)

        ## check to make sure the group has enough currency to cover it.
        amount_required_to_withdraw = request.number_of_impressions * 2 * request.bid_per_impression

        if group.currencyBalance < amount_required_to_withdraw:
            logging.info('Group balance is too low.')
            return AdResponse(response_message='Error: The group CRED balance is too low to create this ad.', response_successful=False)


        # send out a discord alert to the game owner.
        # no bool for this since it should not really be optional
        if game.discord_webhook_admin:
            link = "https://ue4topia.appspot.com/#/games/%s/mode/%s" % (game.key.id(), game_mode.key.id())
            if game_mode.ads_require_approval:
                message = "New ad submitted for review.  %s" %link
            else:
                message = "New ad submitted.  %s" %link
            http_auth = Http()
            headers = {"Content-Type": "application/json"}

            discord_data = { "embeds": [{"title": "New Ad", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)

        ad = adController.create(
            description = request.description,
            title = request.title,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            gameModeKeyId = game_mode.key.id(),
            gameModeTitle = game_mode.onlineSubsystemReference,
            groupKeyId = group.key.id(),
            groupTitle = group.title,
            groupGameKeyId = group_game.key.id(),
            icon_url = request.icon_url,
            textures = request.textures,
            bid_per_impression = request.bid_per_impression,
            number_of_impressions = request.number_of_impressions,
            cost_withdrawn = amount_required_to_withdraw,
            currencyBalance = amount_required_to_withdraw,
            count_shown = 0,
            submitted = True,
            approved = approved,
            active = active,
            rejected = False,
            rejection_message = None,
            refunded = False,
            finalized = False
            )

        ## Create transactions for the withdrawal, and deposit into the ad's wallet
        ## we need two transactions to add to the queue.
        ## One for the Ad
        description = "Ad Created by: %s" %authorized_user.title
        recipient_transaction = transactionController.create(
            amountInt = amount_required_to_withdraw,
            #amountIntGross = amount_required_to_withdraw,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            newBalanceInt = amount_required_to_withdraw,
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            ##userKeyId = authorized_user.key.id(),
            ##firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            adKeyId = ad.key.id(),
            adTitle = ad.title,

            ## we need the gameKeyId so we can set up the game transaction
            gameKeyId = game.key.id(),
            gameTitle = game.title,

            ## we need the groupKey so we can refund the remaining balance
            ## nevermind it is in the ad already.
            #groupKeyId = group.key.id(),
            #groupTitle = group.title,

            ##  transactions are batched and processed all at once.
            transactionType = "ad",
            transactionClass = "creation",
            transactionSender = False,
            transactionRecipient = True,
            submitted = True,
            processed = True,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-primary"
        )
        ## One for the group
        description = "Ad created: %s" %ad.title
        transactionController.create(
            amountInt = -amount_required_to_withdraw,
            ##amount = ndb.FloatProperty(indexed=False) # for display
            ##newBalanceInt = ndb.IntegerProperty(indexed=False)
            ##newBalance = ndb.FloatProperty(indexed=False) # for display
            description = description,
            #userKeyId = authorized_user.key.id(),
            #firebaseUser = authorized_user.firebaseUser,
            ##targetUserKeyId = ndb.IntegerProperty()
            groupKeyId = group.key.id(),
            groupTitle = group.title,
            ##  transactions are batched and processed all at once.
            transactionType = "group",
            transactionClass = "ad_creation",
            transactionSender = True,
            transactionRecipient = False,
            recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_DONATE,
            materialDisplayClass = "md-accent"
        )

        ## then start tasks to process them
        ## don't start a task for the AD.  it is already marked as processeed.

        ## only start pushable tasks.  If they are not pushable, there is already a task running.

        pushable = lockController.pushable("group:%s"%group.key.id())
        if pushable:
            logging.info('group pushable')
            taskUrl='/task/group/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                "key_id": group.key.id()
                                                                            }, countdown=2)




        return AdResponse(response_message="Game Created", response_successful=True)


    @endpoints.method(ADS_COLLECTION_PAGE_RESOURCE, AdsCollection, path='adsCollectionGetPage', http_method='POST', name='collection.get.page')
    def adsCollectionGetPage(self, request):
        """ Get a collection of ads """
        logging.info("adsCollectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return AdsCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return AdsCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return AdsCollection(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        gameModeController = GameModesController()
        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        adController = AdsController()
        groupGameController = GroupGamesController()

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        #sort_order = request.sort_order
        #direction = request.direction

        ads = []

        ## if gameModeKeyId is supplied, get the ads for the game.  Verify game owner
        if request.gameModeKeyId:
            logging.info('gameModeKeyId found')
            # get the gameMOde
            game_mode = gameModeController.get_by_key_id(request.gameModeKeyId)
            if not game_mode:
                logging.info('Game Mode not found.')
                return AdsCollection(response_message='Error: Game Mode not found.', response_successful=False)

            game = gController.get_by_key_id(game_mode.gameKeyId)
            if not game:
                logging.info('Game not found.')
                return AdsCollection(response_message='Error: Game not found.', response_successful=False)

            if game.userKeyId != authorized_user.key.id():
                logging.info('Only the game owner can view ads')
                return AdsCollection(response_message='Error: Only the game owner can view ads.', response_successful=False)

            ads = adController.get_not_final_by_gameModeKeyId(game_mode.key.id())

        ## if groupGameKeyId is supplied get the ads for the group game.  Verify role/permission.
        if request.groupGameKeyId:
            logging.info('groupGameKeyId found')
            #get the group game
            group_game = groupGameController.get_by_key_id(request.groupGameKeyId)
            if not group_game:
                logging.info('group_game not found.')
                return AdsCollection(response_message='Error: group_game not found', response_successful=False)

            ## check if the authenticated user is a member
            group_member = groupUsersController.get_by_groupKeyId_userKeyId(group_game.groupKeyId, authorized_user.key.id())

            if not group_member:
                logging.info('Not a member of this group.')
                return AdsCollection(response_message='Error: Not a member of this group.', response_successful=False)

            # get the role
            group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
            if not group_member_role:
                logging.info('Role not found')
                return AdsCollection(response_message='Error: Role not found.', response_successful=False)

            if not group_member_role.edit_ads:
                logging.info('You do not have sufficient permissions to edit ads for this group.')
                return AdsCollection(response_message='Error: You do not have sufficient permissions to edit ads for this group.', response_successful=False)

            ads = adController.get_not_final_by_groupKeyId_gameKeyId(group_game.groupKeyId, group_game.gameKeyId)

        entity_list = []
        for ad in ads:
            entity_list.append(AdResponse(
                key_id = ad.key.id(),
                created= ad.created.isoformat(' '),
                title = ad.title,
                description = ad.description,
                gameKeyId = ad.gameKeyId,
                gameTitle = ad.gameTitle,
                gameModeKeyId = ad.gameModeKeyId,
                gameModeTitle = ad.gameModeTitle,
                groupKeyId = ad.groupKeyId,
                groupTitle = ad.groupTitle,
                icon_url = ad.icon_url,
                #textures = ad.textures,
                bid_per_impression = ad.bid_per_impression,
                number_of_impressions = ad.number_of_impressions,
                #cost_total = messages.IntegerField(14, variant=messages.Variant.INT32)
                #count_shown = messages.IntegerField(15, variant=messages.Variant.INT32)
                submitted = ad.submitted,
                approved = ad.approved,
                active = ad.active,
                rejected = ad.rejected,
                rejection_message = ad.rejection_message,
                refunded = ad.refunded,
                finalized = ad.finalized
            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = AdsCollection(
            ads = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(AD_RESOURCE, AdResponse, path='adGet', http_method='POST', name='get')
    def adGet(self, request):
        """ Get an ad """
        logging.info("adGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return AdResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return AdResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return AdResponse(response_message='Error: No User Record Found. ', response_successful=False)


        gController = GamesController()
        gameModeController = GameModesController()
        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        adController = AdsController()

        ad_access_granted = False

        ## Get the ad by key
        ad = adController.get_by_key_id(request.key_id)
        if not ad:
            logging.info('no ad record found')
            return AdResponse(response_message='Error: No ad Record Found. ', response_successful=False)

        ## check to see if the user is the owner of the game
        game = gController.get_by_key_id(ad.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return AdResponse(response_message='Error: Game not found.', response_successful=False)

        if game.userKeyId == authorized_user.key.id():
            ad_access_granted = True


        ## or if the user is a member of the group with editing permissions
        ## check if the authenticated user is a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if group_member:
            # get the role
            group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
            if group_member_role:
                logging.info('Role  found')

                if group_member_role.edit_ads:
                    logging.info('You have sufficient permissions to edit ads for this group.')

                    ad_access_granted = True

        if ad_access_granted:
            ## return the ad
            return AdResponse(
                key_id = ad.key.id(),
                title = ad.title,
                description = ad.description,
                gameKeyId = ad.gameKeyId,
                gameTitle = ad.gameTitle,
                gameModeKeyId = ad.gameModeKeyId,
                gameModeTitle = ad.gameModeTitle,
                groupKeyId = ad.groupKeyId,
                groupTitle = ad.groupTitle,
                icon_url = ad.icon_url,
                textures = ad.textures,
                bid_per_impression = ad.bid_per_impression,
                number_of_impressions = ad.number_of_impressions,
                #cost_total = messages.IntegerField(14, variant=messages.Variant.INT32)
                count_shown = ad.count_shown,
                submitted = ad.submitted,
                approved = ad.approved,
                active = ad.active,
                rejected = ad.rejected,
                rejection_message = ad.rejection_message,
                refunded = ad.refunded,
                finalized = ad.finalized,
                response_message='Success:  Ad returned.',
                response_successful=True
            )

    @endpoints.method(AD_RESOURCE, AdResponse, path='adGetHighBid', http_method='POST', name='high.bid.get')
    def adGetHighBid(self, request):
        """ Get an adGetHighBid """
        logging.info("adGetHighBid")

        ## don't need any auth on this
        adController = AdsController()

        logging.info(request.key_id)
        logging.info(type(request.key_id))

        ##
        ad = adController.get_high_bid_by_gameModeKeyId(int(request.key_id))
        if not ad:
            logging.info('no ad record found')
            return AdResponse(response_message='Error: No ad Record Found. ', response_successful=False)

        return AdResponse(
            bid_per_impression = ad.bid_per_impression,
            response_message='Success:  High bid returned.',
            response_successful=True
        )


    @endpoints.method(AD_RESOURCE, AdResponse, path='adsUpdate', http_method='POST', name='update')
    def adsUpdate(self, request):
        """ Update an ad """
        logging.info("adsUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesCollection(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return AdResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        gController = GamesController()
        gameModeController = GameModesController()
        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        adController = AdsController()
        ## get the requested ad

        requested_ad = adController.get_by_key_id(request.key_id)

        if not requested_ad:
            logging.info('requested ad not found')
            return GamesCollection(response_message='Error: No Ad Found. ', response_successful=False)

        ## check if the authenticated user is a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(requested_ad.groupKeyId, authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group.')
            return AdResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('Role not found')
            return AdResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.edit_ads:
            logging.info('You do not have sufficient permissions to edit ads for this group.')
            return AdResponse(response_message='Error: You do not have sufficient permissions to edit ads for this group.', response_successful=False)


        ## any other checks?

        ## if it has not been approved, editing is disabled.

        if requested_ad.approved:
            logging.info('this ad is already approved')
            return AdResponse(response_message='Error: This ad is already approved.  Editing is disabled.', response_successful=False)

        requested_ad.title = request.title
        requested_ad.description = request.description
        requested_ad.icon_url = request.icon_url
        requested_ad.textures = request.textures

        adController.update(requested_ad)

        return AdResponse(response_message='Success.  Ad updated.', response_successful=True)

    @endpoints.method(AD_RESOURCE, AdResponse, path='adsAuthorize', http_method='POST', name='authorize')
    def adsAuthorize(self, request):
        """ Authorize / Reject an ad - PROTECTED"""
        logging.info("adsAuthorize")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GamesCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GamesCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GamesCollection(response_message='Error: No User Record Found. ', response_successful=False)

        gController = GamesController()
        gameModeController = GameModesController()
        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        groupGamesController = GroupGamesController()
        adController = AdsController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        ## get the requested ad

        requested_ad = adController.get_by_key_id(request.key_id)

        if not requested_ad:
            logging.info('requested ad not found')
            return GamesCollection(response_message='Error: No Ad Found. ', response_successful=False)

        ## only the game owner can perform this action
        game = gController.get_by_key_id(requested_ad.gameKeyId)
        if not game:
            logging.info('Game not found.')
            return AdResponse(response_message='Error: Game not found.', response_successful=False)

        if game.userKeyId != authorized_user.key.id():
            logging.info('only the game owner can perform this action .')
            return AdResponse(response_message='Error: only the game owner can perform this action.', response_successful=False)

        ## in either case, we'll want to check to see if we need to send out a discord alert
        group_game = groupGamesController.get_by_groupKeyId_gameKeyId(requested_ad.groupKeyId, game.key.id())

        ## What are we doing?
        if request.approved:
            logging.info("approving it")

            requested_ad.approved = True
            requested_ad.active = True
            adController.update(requested_ad)

            ## also send out a message to the group discord.
            ## we need the group game for this

            if group_game:
                if group_game.discord_subscribe_game_ad_status_changes:

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/groups/%s/games/%s/ads/%s" % (requested_ad.groupKeyId, requested_ad.groupGameKeyId, requested_ad.key.id())
                    message = "Ad approved:  %s" % (link)
                    discord_data = { "embeds": [{"title": "Ad approved", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group_game.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)


            return AdResponse(response_message='Success:  Ad approved.', response_successful=True)



        else:
            logging.info("rejecting it")

            requested_ad.rejected = True
            requested_ad.approved = False
            requested_ad.active = False
            requested_ad.rejection_message = request.rejection_message


            ## issue a refund - since it has never been live, we don't need to worry about transactions here.
            ## just a deposit transaction into the group

            ## Create transactions for the withdrawal, and deposit into the ad's wallet
            ## we need two transactions to add to the queue.
            ## One for the Ad
            description = "Ad rejection refund for: %s" % requested_ad.title
            recipient_transaction = transactionController.create(
                amountInt = requested_ad.currencyBalance,
                #amountIntGross = amount_required_to_withdraw,
                ##amount = ndb.FloatProperty(indexed=False) # for display
                ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                ##newBalance = ndb.FloatProperty(indexed=False) # for display
                description = description,
                ##userKeyId = authorized_user.key.id(),
                ##firebaseUser = authorized_user.firebaseUser,
                ##targetUserKeyId = ndb.IntegerProperty()
                groupKeyId = group_game.groupKeyId,
                groupTitle = group_game.groupTitle,

                ##  transactions are batched and processed all at once.
                transactionType = "group",
                transactionClass = "ad_refund",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_AD_REJECTED,
                materialDisplayClass = "md-primary"
            )

            ## then start tasks to process them
            ## only start pushable tasks.  If they are not pushable, there is already a task running.
            pushable = lockController.pushable("group:%s"%group_game.groupKeyId)
            if pushable:
                logging.info('group pushable')
                taskUrl='/task/group/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='groupTransactionProcess', params={
                                                                                    "key_id": group_game.groupKeyId
                                                                                }, countdown=2)


            requested_ad.currencyBalance = 0
            requested_ad.refunded = True
            requested_ad.finalized = True

            adController.update(requested_ad)

            ## also send out a message to the group discord.

            if group_game:
                if group_game.discord_subscribe_game_ad_status_changes:
                    message = "Ad rejected" % (authorized_user.title, link)
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/groups/%s/ads/%s" % (requested_ad.groupKeyId, requested_ad.key.id())
                    discord_data = { "embeds": [{"title": "Ad rejected", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group_game.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)

            return AdResponse(response_message='Success:  Ad rejected.', response_successful=True)
