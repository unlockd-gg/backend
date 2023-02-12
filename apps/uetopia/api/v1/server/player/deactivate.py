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

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
#from apps.uetopia.utilities.server_player_deactivate import deactivate_player
from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class DeactivatePlayerHandler(BaseHandler):
    def post(self, userid):
        """
        Deactivate a user
        Requires http headers:  Key, Sign
        Requires POST parameters:  userid, currency_balance, rank, nonce
        """

        serverController = ServersController()
        uController = UsersController()
        spController = ServerPlayersController()

        server = serverController.verify_signed_auth(self.request)

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

                user = UsersController().get_by_firebaseUser(claims['user_id'])

                if not user:
                    logging.info('no user record found')
                    return self.render_json_response(
                        authorization = True,
                        player_authorized = False,
                        user_key_id = incoming_userid,
                        player_userid = incoming_userid,
                    )

                # check to see if there is a server user member record
                server_player_member = spController.get_server_user(server.key.id(), user.key.id() )

                if server_player_member:
                    logging.info('server_player_member found')

                    ## start a task to handle it.
                    ## we need a delay because usually the transfer request comes milliseconds before this one.
                    ## we need to make sure that the transfer has already been processed.


                    taskUrl='/task/server/player/deauthorize'
                    taskqueue.add(url=taskUrl, queue_name='serverDeauthorize', params={
                                                                                            "key_id": server_player_member.key.id(),
                                                                                            "new_rank": self.request.get('rank', 1600),
                                                                                            "currency_balance": self.request.get('currency_balance', 0)
                                                                                        }, countdown=2)

                else:
                    logging.info('server_player_member NOT found')
                    authorized = False
                    auth_deny_reason = "Authorization: record missing"

            else:
                logging.info('no access token found - doing it the old way - deprecated')

                player_userid = userid #self.request.get('userid', None)

                logging.info("incoming player_userid: %s" % player_userid)

                if player_userid:
                    logging.info('userid found in post')

                    authenticated_user = uController.get_by_key_id(int(userid))

                    if authenticated_user:
                        logging.info('user found')

                        # first check to see if there is a server user member record
                        server_player_member = spController.get_server_user(server.key.id(), authenticated_user.key.id() )

                        if server_player_member:
                            logging.info('server_player_member found')

                            ## start a task to handle it.
                            ## we need a delay because usually the transfer request comes milliseconds before this one.
                            ## we need to make sure that the transfer has already been processed.


                            taskUrl='/task/server/player/deauthorize'
                            taskqueue.add(url=taskUrl, queue_name='serverDeauthorize', params={
                                                                                                    "key_id": server_player_member.key.id(),
                                                                                                    "new_rank": self.request.get('rank', 1600),
                                                                                                    "currency_balance": self.request.get('currency_balance', 0)
                                                                                                }, countdown=2)

                        else:
                            logging.info('server_player_member NOT found')
                            authorized = False
                            auth_deny_reason = "Authorization: record missing"

                    else:
                        logging.info('user NOT found using userid')

            return self.render_json_response(
                authorization = True,
                user_key_id = userid
            )
