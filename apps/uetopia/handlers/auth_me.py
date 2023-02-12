import logging
import json
from apps.handlers import BaseHandler
#from google.appengine.api import users
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from google.appengine.api import urlfetch
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.user_login_tokens import UserLoginTokensController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class IndexHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def get(self):
        """ Static Index

        """
        #user = users.get_current_user()
        usersController = UsersController()
        ultController = UserLoginTokensController()

        ## check access token - get user by token
        claims = google.oauth2.id_token.verify_firebase_token(self.request.get('access_token'), HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return self.render_json_response(
                auth=True,
                id=None,
                AuthTicket = None
                )
        else:
            logging.info('firebase auth')
            authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('user not found')
                return self.render_json_response(
                    auth=True,
                    id=None,
                    AuthTicket = None
                    )

        #user_token = ultController.get_by_access_token(self.request.get('access_token'))

        #if not user_token:

        ## get the IP address to use from our socket.io server:
        #SocketIpAddress = "http://uetopia.herokuapp.com"

        return self.render_json_response(
            auth=True,
            id=str(authorized_user.key.id()),
            ##userId=user_token.userKeyId,
            AuthTicket = "testTicket",
            SocketIpAddress = HEROKU_SOCKETIO_SERVER,
            firebaseUser = authorized_user.firebaseUser
            )
