import logging
import datetime
import string
import json
from httplib2 import Http
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## CONTROLLERS
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

class GetVendorHandler(BaseHandler):
    def post(self, vendorKeyId):
        """
        Get a vendor
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, vendorKeyId
        """

        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()
        userController = UsersController()


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


        entity = vendorController.get_by_key_id(int(vendorKeyId))

        if not entity:
            logging.info('vendor not found')
            return self.render_json_response(authorization = True, response_message="vendor not found", key_id =vendorKeyId, success=False)




        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor found",
            title = entity.title,
            description = entity.description,
            vendorKeyId = entity.vendorKeyId,
            vendorTypeKeyId = entity.vendorTypeKeyId,
            coordLocationX = entity.coordLocationX,
            coordLocationY = entity.coordLocationY,
            coordLocationZ = entity.coordLocationZ,
            forwardVecX = entity.forwardVecX,
            forwardVecY = entity.forwardVecY,
            forwardVecZ = entity.forwardVecZ,
            createdByUserKeyId = str(entity.createdByUserKeyId),
            buyingMax = entity.buyingMax,
            sellingMax = entity.sellingMax,
            #transactionTaxPercentageToServer = vendor_type.transactionTaxPercentageToServer,
            #engineActorAsset = vendor_type.engineActorAsset,
        )
