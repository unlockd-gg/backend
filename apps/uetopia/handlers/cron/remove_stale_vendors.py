import logging
import datetime
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import users

from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.handlers import BaseHandler
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.vendor_types import VendorTypesController
from apps.uetopia.controllers.vendors import VendorsController
from apps.uetopia.controllers.vendor_items import VendorItemsController
from apps.uetopia.controllers.drops import DropsController
from apps.uetopia.controllers.games import GamesController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class RemoveStaleVendorsHandler(BaseHandler):
    def get(self):
        logging.info('Cron RemoveStaleVendorsHandler')

        userController = UsersController()
        gameController = GamesController()
        gamePlayerController = GamePlayersController()

        vendorController = VendorsController()
        vendorItemController = VendorItemsController()
        dropsController = DropsController()

        lockController = TransactionLockController()
        transactionController = TransactionsController()

        expired_vendors = vendorController.get_expired()

        ## set up globabls for all drops
        now = datetime.datetime.now()
        thirty_days = datetime.timedelta(days=30)
        thirty_days_from_now = now + thirty_days
        expirationDate = thirty_days_from_now

        ## keep track of total items removed also
        total_items_deleted = 0

        ## THIS IS SET TO GET ONLY A SINGLE VENDOR TESTING
        ## REMEMBER TO PUT 1000 BEFORE LIVE

        for expired_vendor in expired_vendors:
            logging.info('found expired vendor')

            ## we only want to look up this vendor's owner once:
            vendor_owner_game_player = gamePlayerController.get_by_gameKeyId_userKeyId(expired_vendor.gameKeyId, expired_vendor.createdByUserKeyId)


            ## get the game, so we can send a discord push
            this_vendors_game = gameController.get_by_key_id(expired_vendor.gameKeyId)
            if this_vendors_game:
                logging.info('found the vendors game')

                ## get the vendor gamekeyID so it can be refunded

                ## get all of the vendor items
                this_vendors_items = vendorItemController.get_by_vendorKeyId(expired_vendor.key.id())

                ## keep track of what happeend
                this_vendors_items_refunded_to_owner = 0
                this_vendors_items_refunded_to_others = 0
                this_vendors_currency_returned_to_owner = 0
                this_vendors_currency_returned_to_others = 0

                for this_vendors_item in this_vendors_items:
                    logging.info('found an item')

                    ## make sure it has a DTID first.
                    if this_vendors_item.dataTableId:
                        logging.info('found dtid')

                        ## build out the data json

                        ## It needs to look like:
                        """
                        {
                        	"Quantity": 1,
                        	"DTID": 1002,
                        	"Tier": 0,
                        	"attributes": [
                        		{
                        			"0": 0.33600878715515137
                        		},
                        		{
                        			"1": 0.96667385101318359
                        		},
                        		{
                        			"2": 0.5047760009765625
                        		},
                        		{
                        			"3": 0.87145590782165527
                        		},
                        		{
                        			"4": 0.10803556442260742
                        		},
                        		{
                        			"5": 0.58336138725280762
                        		},
                        		{
                        			"6": 0.59862065315246582
                        		},
                        		{
                        			"7": 0.11719083786010742
                        		},
                        		{
                        			"8": 0.25284624099731445
                        		},
                        		{
                        			"9": 0.61571073532104492
                        		}
                        	]
                        }
                        """

                        ## we already have the attributes json, so let's just parse that, and add the new fields.
                        jsonobject = json.loads(this_vendors_item.attributes)

                        jsonobject["Tier"] = this_vendors_item.tier
                        jsonobject["Quantity"] = this_vendors_item.quantityAvailable
                        jsonobject["DTID"] = this_vendors_item.dataTableId

                        jsonstring = json.dumps(jsonobject)

                        logging.info(jsonstring)





                        if this_vendors_item.buyingOffer:
                            logging.info('found an offer - sending it back to its owner')

                            ## get the gamePlayer for the owner
                            game_player = gamePlayerController.get_by_gameKeyId_userKeyId(expired_vendor.gameKeyId, this_vendors_item.buyingOfferUserKeyId)
                            if game_player:
                                logging.info('got game player')

                                this_vendors_items_refunded_to_others = this_vendors_items_refunded_to_others +1

                                dropsController.create(
                                    expirationDate = expirationDate,
                                    title = this_vendors_item.title,
                                    description = this_vendors_item.description,
                                    gameKeyId = this_vendors_item.gameKeyId,
                                    gameTitle = this_vendors_item.gameTitle,
                                    userKeyId = this_vendors_item.buyingOfferUserKeyId,
                                    #userTitle = ndb.StringProperty(indexed=False)

                                    gamePlayerKeyId = game_player.key.id(),
                                    #gamePlayerTitle = game_player.title,

                                    #uiIcon = jsonobject['uiIcon'],
                                    data = jsonstring
                                )
                                ## push discrod message to the offered player

                        elif this_vendors_item.claimableAsCurrency:

                            ## deal with claimableAsCurrency - when claimable, buyingOffer is false
                            if this_vendors_item.pricePerUnit > 0:
                                logging.info ('found this_vendors_item.claimableAsCurrency')

                                ## get the gamePlayer for the owner
                                game_player = gamePlayerController.get_by_gameKeyId_userKeyId(expired_vendor.gameKeyId, this_vendors_item.buyingOfferUserKeyId)
                                if game_player:
                                    logging.info('got game player')

                                    ## Transaction for the item owner
                                    description = "Vendor expired with a claimable balance"

                                    amountClaimable = this_vendors_item.pricePerUnit * this_vendors_item.quantityAvailable

                                    transaction = TransactionsController().create(
                                        userKeyId = game_player.userKeyId,
                                        firebaseUser = game_player.firebaseUser,
                                        description = description,
                                        amountInt = amountClaimable,
                                        transactionType = "user",
                                        transactionClass = "vendorexpiration",
                                        transactionSender = False,
                                        transactionRecipient = True,
                                        submitted = True,
                                        processed = False,
                                        materialIcon = MATERIAL_ICON_REFERRAL,
                                        materialDisplayClass = "md-primary"
                                        )

                                    lockController = TransactionLockController()

                                    pushable = lockController.pushable("user:%s"%game_player.userKeyId)
                                    if pushable:
                                        logging.info('referral_user pushable')
                                        taskUrl='/task/user/transaction/process'
                                        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                            "key_id": game_player.userKeyId
                                                                                                        }, countdown=2)

                        else:
                            logging.info('This was a regular vendor item.')

                            # make sure it exists
                            if vendor_owner_game_player:
                                logging.info('we have the vendor owner')

                                this_vendors_items_refunded_to_owner = this_vendors_items_refunded_to_owner +1

                                dropsController.create(
                                    expirationDate = expirationDate,
                                    title = this_vendors_item.title,
                                    description = this_vendors_item.description,
                                    gameKeyId = this_vendors_item.gameKeyId,
                                    gameTitle = this_vendors_item.gameTitle,
                                    userKeyId = this_vendors_item.userKeyId,
                                    #userTitle = ndb.StringProperty(indexed=False)

                                    gamePlayerKeyId = vendor_owner_game_player.key.id(),
                                    #gamePlayerTitle = vendor_owner_game_player.userTitle,

                                    #uiIcon = jsonobject['uiIcon'],
                                    data = jsonstring
                                )

                    ## Done with this item - delete it
                    vendorItemController.delete(this_vendors_item)
                    total_items_deleted = total_items_deleted +1

                ## deal with vendorCurrency

                if expired_vendor.vendorCurrency > 0:
                    logging.info('found vendor currency.  Returning it to the owner.')
                    this_vendors_currency_returned_to_owner = expired_vendor.vendorCurrency

                    ## Transaction for the vendor owner
                    description = "Vendor expired with a balance"

                    transaction = TransactionsController().create(
                        userKeyId = expired_vendor.createdByUserKeyId,
                        firebaseUser = vendor_owner_game_player.firebaseUser,
                        description = description,
                        amountInt = this_vendors_currency_returned_to_owner,
                        transactionType = "user",
                        transactionClass = "vendorexpiration",
                        transactionSender = False,
                        transactionRecipient = True,
                        submitted = True,
                        processed = False,
                        materialIcon = MATERIAL_ICON_REFERRAL,
                        materialDisplayClass = "md-primary"
                        )

                    lockController = TransactionLockController()

                    pushable = lockController.pushable("user:%s"%expired_vendor.createdByUserKeyId)
                    if pushable:
                        logging.info('referral_user pushable')
                        taskUrl='/task/user/transaction/process'
                        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                            "key_id": expired_vendor.createdByUserKeyId
                                                                                        }, countdown=2)




                ## push discord message to the player owner with a summary

                summary_message = "%s items and %s CRED were sent back to you.  %s items were sent back to others." %(this_vendors_items_refunded_to_owner, this_vendors_currency_returned_to_owner, this_vendors_items_refunded_to_others)
                ## push discord msg to the vendor
                if expired_vendor.discordWebhook:
                    ## do a discord push
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())
                    headers = {"Content-Type": "application/json"}

                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Vendor: %s Expired: %s" %(expired_vendor.title, summary_message)
                    ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Vendor expired", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(expired_vendor.discordWebhook,
                                      "POST",
                                      data,
                                      headers=headers)

                    ## push discord message to the game with a summary
                    message = "Vendor: %s expired and was deleted. Update vendors monthly to keep them alive." %(expired_vendor.title)
                    ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Vendor expired", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(this_vendors_game.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)

                ## convert this vendor into a drop if possible
                if expired_vendor.thisVendorDTID:
                    logging.info('found vendor DTID')

                    jsonobject = {}
                    jsonobject["Tier"] = -1
                    jsonobject["Quantity"] = 1
                    jsonobject["DTID"] = expired_vendor.thisVendorDTID
                    jsonobject['attributes'] = [] #empty array so lookup will succeed, but no entries, so nothing is added

                    jsonstring = json.dumps(jsonobject)

                    logging.info(jsonstring)

                    dropsController.create(
                        expirationDate = expirationDate,
                        title = expired_vendor.title,
                        description = expired_vendor.description,
                        gameKeyId = expired_vendor.gameKeyId,
                        gameTitle = expired_vendor.gameTitle,
                        userKeyId = expired_vendor.createdByUserKeyId,
                        #userTitle = ndb.StringProperty(indexed=False)

                        gamePlayerKeyId = vendor_owner_game_player.key.id(),
                        #gamePlayerTitle = vendor_owner_game_player.userTitle,

                        #uiIcon = jsonobject['uiIcon'],
                        data = jsonstring
                    )





                ## and delete it
                vendorController.delete(expired_vendor)






        vendorcount = len(expired_vendors)

        return self.render_json_response(
            vendorcount= vendorcount,
            total_items_deleted = total_items_deleted
        )
