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

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class DeleteVendorHandler(BaseHandler):
    def post(self, vendorKeyId):
        """
        Create a vendor
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, userKeyId, vendorKeyId
        """

        gamesController = GamesController()
        serverController = ServersController()
        vendorTypeController = VendorTypesController()
        vendorController = VendorsController()
        userController = UsersController()
        vendorItemController = VendorItemsController()


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
        if not authorized_user:
            logging.info('no vendor found')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="vendor not found"
            )

        ## make sure the vendor is owned by the player requesting deletion
        if authorized_user.key.id() != vendor.createdByUserKeyId:
            logging.info('cannot delete this vendor.  you are not the owner.')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="cannot delete this vendor.  you are not the owner."
            )


        ## make sure there are no pending items or transactions
        vendor_items = vendorItemController.get_by_vendorKeyId(vendor.key.id())
        if len(vendor_items) > 0:
            logging.info('cannot delete this vendor.  it still has items listed')
            return self.render_json_response(
                authorization = True,
                success=False,
                response_message="cannot delete this vendor.  it still has items listed"
            )

        if vendor.discordWebhook:
            ## do a discord push
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Vendor: %s deleted" % vendor.title
            ##url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
            discord_data = { "embeds": [{"title": "Vendor Deleted", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(vendor.discordWebhook,
                              "POST",
                              data,
                              headers=headers)

        vendorController.delete(vendor)

        return self.render_json_response(
            authorization = True,
            success=True,
            response_message="vendor deleted"
        )
