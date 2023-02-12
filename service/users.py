import endpoints
import logging
import uuid
import urllib
import json
import datetime
import google.oauth2.id_token
import google.auth.transport.requests
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
from protorpc import remote
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

##from apps.uetopia.providers import firebase_helper



from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.user_login_tokens import UserLoginTokensController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController

from apps.uetopia.models.users import Users, UserResponse, USER_RESOURCE, UserCollection, USER_COLLECTION_PAGE_RESOURCE


from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ClientConnectResponse(messages.Message):
    """ a client's data """
    user_id = messages.StringField(1)
    refresh_token = messages.BooleanField(2) ## should we do a refresh and try again?
    response_message = messages.StringField(4)
    custom_title = messages.StringField(5)
    access_token = messages.StringField(6)
    agreed_with_terms = messages.BooleanField(7)
    response_successful = messages.BooleanField(50)


@endpoints.api(name="users", version="v1", description="Users API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class UsersApi(remote.Service):
    @endpoints.method(USER_RESOURCE, ClientConnectResponse, path='clientSignIn', http_method='POST', name='client.signin')
    def clientSignIn(self, request):
        """ Connect and verify a user's login token - This is called when a user signs in. """
        logging.info('clientSignIn')

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response
        else:
            logging.info('claims verified')

            name = "Unknown"

            try:
                name = claims['name']
            except:
                name = "Unknown"

            try:
                userEmail = claims['email']
            except:
                userEmail = ""

            ## get this user or create if needed
            uController = UsersController()
            lockController = TransactionLockController()

            authorized_user = uController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('no user record found')

                createable = lockController.pushable("user-create:%s"%claims['user_id'])
                if createable:
                    logging.info('creating new user')

                    #rController = RolesController()

                    ## assign applicant
                    #applicant_role = rController.get_applicant_role()

                    logging.info(claims)

                    apiKey = uController.create_unique_api_key()
                    apiSecret = uController.key_generator()

                    try:
                        picture = claims['picture']
                    except:
                        picture = None



                    authorized_user = uController.create(firebaseUser=claims['user_id'],
                                                online=True,
                                                admin=False,
                                                #roleKeyId=applicant_role.key.id(),
                                                apiKey = apiKey,
                                                apiSecret = apiSecret,
                                                ## TODO set up user defaults here
                                                email = userEmail,
                                                picture = picture,
                                                sign_in_provider = claims['firebase']['sign_in_provider'],
                                                title = name,
                                                currencyBalance = 0,
                                                region = "us-central1", ## assigning default region - getting too many users hitting an error because of this.
                                                profile_saved=False,
                                                agreed_with_terms = False)

                    ## Push a chat out to slack
                    #http_auth = Http()
                    #headers = {"Content-Type": "application/json"}
                    #URL = "https://hooks.slack.com/services/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"
                    #message = "New User: %s | %s " % (name, claims['email'])
                    #slack_data = {'text': message}
                    #data=json.dumps(slack_data)
                    #resp, content = http_auth.request(URL,
                    #                  "POST",
                    #                  data,
                    #                  headers=headers)

                    # push a chat out to discord
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    URL = "https://discordapp.com/api/webhooks/296875502667563010/unl46-TDtugd_p7b-DF1LUsMiEXv3R2D-0PVUmDTiSmwk04GF61MVH10J-KD_NkaLucy"
                    message = "%s | %s " % (name, userEmail)
                    discord_data = { "embeds": [{"title": "New User", "url": "https://example.com", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(URL,
                                      "POST",
                                      data,
                                      headers=headers)

                    ## FREE MONEY!!!!
                    description = "Thanks for joining! Here's some CRED to get you started."

                    ## Create a transaction for the deposit -user
                    transaction = TransactionsController().create(
                        userKeyId = authorized_user.key.id(),
                        firebaseUser = authorized_user.firebaseUser,
                        description = description,
                        ##confirmations = 0,
                        amountInt = CRED_BONUS_NEW_USER_ACCOUNT_CREATION,
                        #serverKeyId = server.key.id(),
                        #serverTitle = server.title,
                        ##amount = currency_hold / 100000000. * -1,
                        #newBalanceInt = authorized_user.currencyBalance,
                        #newBalance = float(authorized_user.currencyBalance) / 100000000.
                        transactionType = "user",
                        transactionClass = "new account creation",
                        transactionSender = False,
                        transactionRecipient = True,
                        submitted = True,
                        processed = False,
                        materialIcon = MATERIAL_ICON_NEW_USER_PAYMENT,
                        materialDisplayClass = "md-primary"
                        )



                    pushable = lockController.pushable("user:%s"%authorized_user.key.id())
                    if pushable:
                        logging.info('user pushable')
                        taskUrl='/task/user/transaction/process'
                        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                            "key_id": authorized_user.key.id()
                                                                                        }, countdown=2)

                    ## push an alert out to firebase
                    taskUrl='/task/user/alert/create'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                                    'material_icon': MATERIAL_ICON_NEW_USER_PAYMENT,
                                                                                    'importance': 'md-primary',
                                                                                    ## TODO this message can be more helpful
                                                                                    'message_text': description,
                                                                                    'action_button_color': 'primary',
                                                                                    'action_button_sref': '#/user/transactions'
                                                                                    }, countdown = 10,)
                else:
                    logging.info('not creating new user')

            else:
                logging.info('user found')

            ## deal with the refreshToken which we need to store if the request comes in via the UE client.
            ## on the web interface, firebase handles this directly and automatically
            refreshToken = request.refreshToken

            if refreshToken:
                logging.info('found refreshToken')
                authorized_user.refreshToken = refreshToken
                uController.update(authorized_user)
            else:
                logging.info('NO refreshToken found')

            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)

        response = ClientConnectResponse(
            user_id = claims['user_id'],
            agreed_with_terms = authorized_user.agreed_with_terms,
            refresh_token = False,
            response_message='Connected successfully.',
            response_successful=True
        )

        return response

    @endpoints.method(USER_RESOURCE, ClientConnectResponse, path='clientConnect', http_method='POST', name='client.connect')
    def clientConnect(self, request):
        """ Connect and verify a user's login token - This is called when a user loads the website and is already logged in. """
        logging.info('clientConnect')

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response
        else:
            logging.info('claims verified')


            try:
                name = claims['name']
            except:
                name = claims['email']

            ## get this user or create if needed
            uController = UsersController()
            lockController = TransactionLockController()

            authorized_user = uController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.warning('no user record found - this can happen on first sign in')

                response = ClientConnectResponse(
                    user_id = claims['user_id'],
                    agreed_with_terms = False,
                    refresh_token = False,
                    response_message='No user record found',
                    response_successful=False
                )
                ## Users do not get created in this call ever.  It causes occasional duplicates because of the way firebase spams refreshes on the login screen.
                return response
            else:
                logging.info('user found')
                logging.info(authorized_user.title)


            user_dirty = False

            ## deal with the refreshToken which we need to store if the request comes in via the UE client.
            ## on the web interface, firebase handles this directly and automatically
            refreshToken = request.refreshToken

            if refreshToken:
                logging.info('found refreshToken')
                authorized_user.refreshToken = refreshToken
                #uController.update(authorized_user)
                user_dirty = True
            else:
                logging.info('NO refreshToken found')

            if authorized_user.twitch_streamer:
                logging.info('twitch streamer found - checking stream status')

                FIREBASE_SCOPES = [
                    'https://www.googleapis.com/auth/firebase.database',
                    #'https://www.googleapis.com/auth/firebase.readonly',
                    #'https://www.googleapis.com/auth/cloud-platform',
                    #'https://www.googleapis.com/auth/firebase',
                    'https://www.googleapis.com/auth/securetoken',
                    'https://www.googleapis.com/auth/userinfo.email']

                #credentials = GoogleCredentials.get_application_default().create_scoped(FIREBASE_SCOPES)
                credentials = AppAssertionCredentials(FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())

                headers = {"Content-Type": "application/json", "Client-ID": TWITCH_CLIENT_ID} # , "user_id": authorized_user.twitch_channel_id
                #URL = "https://api.twitch.tv/helix/streams/%s" % authorized_user.twitch_channel_id
                URL = "https://api.twitch.tv/helix/streams?user_login=%s" % authorized_user.twitch_channel_id

                try:
                    resp, content = http_auth.request(URL,
                                        "GET",
                                      ##"PUT", ## Write or replace data to a defined path,
                                      #user_json,
                                      headers=headers)

                    #logging.info(resp)
                    logging.info(content)
                    stream_info_json = json.loads(content)
                    if stream_info_json['data']:
                        logging.info('stream data found')

                        if len(stream_info_json['data']) > 0:
                            logging.info('found something inside data')
                            for stream_data in stream_info_json['data']:
                                logging.info('found stream within data')
                                if not authorized_user.twitch_currently_streaming:
                                    user_dirty = True
                                authorized_user.twitch_currently_streaming = True
                                authorized_user.twitch_stream_game = stream_data['game_id']
                                authorized_user.twitch_stream_viewers = stream_data['viewer_count']
                        else:
                            if authorized_user.twitch_currently_streaming:
                                user_dirty = True
                            authorized_user.twitch_currently_streaming = False
                    else:
                        if authorized_user.twitch_currently_streaming:
                            user_dirty = True
                        authorized_user.twitch_currently_streaming = False
                except:
                    if authorized_user.twitch_currently_streaming:
                        user_dirty = True
                    authorized_user.twitch_currently_streaming = False
                    authorized_user.twitch_stream_game = ""
                    authorized_user.twitch_stream_viewers = 0

            if user_dirty:
                logging.info('user dirty')
                uController.update(authorized_user)


            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)


        response = ClientConnectResponse(
            user_id = claims['user_id'],
            agreed_with_terms = authorized_user.agreed_with_terms,
            refresh_token = False,
            response_message='Connected successfully.',
            response_successful=True
        )

        return response

    @endpoints.method(USER_RESOURCE, UserResponse, path='me', http_method='POST', name='me')
    def me(self, request):
        """ Deprecated - unused """
        logging.info("Me")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = UserResponse(
                key_id = None,
                title = None,
                description = None,
                profile_saved = None,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        # [START create_entity]
        data = request.get_json()

        current_user = endpoints.get_current_user()
        user = current_user
        logging.info("current_user: %s" % current_user)
        if not current_user:
            return UserResponse(response_message='Error: Oauth2 Authentication Missing.', response_successful=False)

        usersController = UsersController()

        entity = usersController.get_by_googleUser(str(user))
        if entity:
            response = UserResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                profile_saved = entity.profile_saved,
                developer = entity.developer,
                apiKey = entity.apiKey,
                apiSecret = entity.apiSecret,
                admin = entity.admin,
                currencyBalance = entity.currencyBalance,
                region = entity.region,
                response_message='Success.',
                response_successful=True
            )
        else:
            response = UserResponse(
                key_id = None,
                title = None,
                description = None,
                profile_saved = None,
                response_message='Not Found.',
                response_successful=False
            )

        return response

    @endpoints.method(USER_RESOURCE, UserResponse, path='usersGet', http_method='POST', name='get')
    def usersGet(self, request):
        """ Get a list of users """
        logging.info("usersGet")

        uController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return UserResponse(response_message='Error: No User Record Found. ', response_successful=False)


        if request.key_id:
            entity = uController.get_by_key_id(int(request.key_id))
        elif request.email:
            entity = uController.get_by_email(request.email)
        else:
            return UserResponse(response_message="key_id is required")

        if not entity:
            return UserResponse(response_message="No user was found.")

        if authorized_user.admin:
            logging.info('admin detected')
            response = UserResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                firebaseUser = entity.firebaseUser,
                email = entity.email,
                picture = entity.picture,
                sign_in_provider = entity.sign_in_provider,
                currencyBalance = entity.currencyBalance,
                response_message='Success.  User returned.',
                response_successful=True
            )

            return response
        else:
            logging.info('admin NOT detected')
            response = UserResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                #firebaseUser = entity.firebaseUser,
                email = entity.email,
                picture = entity.picture,
                sign_in_provider = entity.sign_in_provider,
                #currencyBalance = entity.currencyBalance,
                response_message='Success.  User returned.',
                response_successful=True
            )

            return response


    @endpoints.method(USER_RESOURCE, UserResponse, path='usersUpdate', http_method='POST', name='update')
    def usersUpdate(self, request):
        """ Update a user """
        logging.info("usersUpdate")
        logging.info(request)

        usersController = UsersController()
        groupUserController = GroupUsersController()
        groupController = GroupsController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = usersController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return UserResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not request.key_id:

            logging.info('no key_id found doing a self update.')

            if request.agreed_with_terms:
                logging.info('agreement accepted - updating user record and exiting')
                if not authorized_user.agreed_with_terms:
                    authorized_user.agreed_with_terms = True
                    usersController.update(authorized_user)
                    return UserResponse(response_message="Success.", response_successful=True)
                else:
                    ## they may have submitted again - avoid erasing all the user data.

                    return UserResponse(response_message="Success.", response_successful=True)

            #logging.info(request.title)
            #logging.info(request.description)

            ## prevent users from spamming this
            if authorized_user.profile_saved:
                now = datetime.datetime.now()
                time_since_last_update = now - authorized_user.modified

                duration_seconds = time_since_last_update.days * 86400 + time_since_last_update.seconds
                if duration_seconds < PROFILE_UPDATE_INTERVAL_MINIMUM_SECONDS:
                    logging.info("you cannot update your profile so frequently.")
                    return UserResponse(response_message="You cannot update your profile so frequently.", response_successful=False)

            ## task to rename the user subobjects

            if authorized_user.title != request.title:
                logging.info('found different user title - TODO starting a task to rename user subobjects')

                ## we need to do:
                # game player
                #taskUrl='/task/game/player/user_batch_rename'
                #taskqueue.add(url=taskUrl, queue_name='userRenameSubprocess', params={'key_id': authorized_user.key.id()}, countdown = 2,)

                # server player ?
                # user relationships - no make it a nickname or something
                # team members ?
                # group users - does not need a batch process.

                # chat channel subscribers?

            authorized_user.title = request.title
            authorized_user.description = request.description


            ## if they chose a personality, give them 10 points for it.
            ## only allow it the first time
            if not authorized_user.profile_saved:
                if request.personality:
                    if request.personality == "killer":
                        authorized_user.playstyle_killer = 10
                    elif request.personality == "achiever":
                        authorized_user.playstyle_achiever = 10
                    elif request.personality == "explorer":
                        authorized_user.playstyle_explorer= 10
                    elif request.personality == "socializer":
                        authorized_user.playstyle_socializer = 10

            ## Check to see if developer was activated this request
            if not authorized_user.developer:
                if request.developer:
                    try:
                        name = claims['name']
                    except:
                        name = claims['email']
                    # push a chat out to discord
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    URL = "https://discordapp.com/api/webhooks/296875502667563010/unl46-TDtugd_p7b-DF1LUsMiEXv3R2D-0PVUmDTiSmwk04GF61MVH10J-KD_NkaLucy"
                    message = "%s | %s " % (name, claims['email'])
                    discord_data = { "embeds": [{"title": "Developer Enabled", "url": "https://example.com", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(URL,
                                      "POST",
                                      data,
                                      headers=headers)

            # developer bool is just for show, every user already has a key/secret created on first login.
            authorized_user.developer = request.developer


            authorized_user.profile_saved = True
            authorized_user.region = request.region

            authorized_user.gsp_advertisements = request.gsp_advertisements
            authorized_user.gsp_totally_free = request.gsp_totally_free
            authorized_user.gsp_free_to_play = request.gsp_free_to_play
            authorized_user.gsp_subscription = request.gsp_subscription
            authorized_user.gsp_sticker_price_purchase = request.gsp_sticker_price_purchase

            authorized_user.twitch_streamer = request.twitch_streamer
            authorized_user.twitch_channel_id = request.twitch_channel_id

            authorized_user.opt_out_email_promotions = request.opt_out_email_promotions
            authorized_user.opt_out_email_alerts = request.opt_out_email_alerts

            authorized_user.defaultTeamTitle = request.defaultTeamTitle
            authorized_user.discord_webhook = request.discord_webhook
            authorized_user.discord_subscribe_errors = request.discord_subscribe_errors
            authorized_user.discord_subscribe_transactions = request.discord_subscribe_transactions
            authorized_user.discord_subscribe_consignments = request.discord_subscribe_consignments

            if authorized_user.discord_webhook:
                logging.info('discord webhook enabled')

                # push a chat out to discord
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                #URL = "https://discordapp.com/api/webhooks/296875502667563010/unl46-TDtugd_p7b-DF1LUsMiEXv3R2D-0PVUmDTiSmwk04GF61MVH10J-KD_NkaLucy"
                message = "Profile Updated."
                discord_data = { "embeds": [{"title": "Profile Updated", "url": "https://uetopia.com", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(authorized_user.discord_webhook,
                                  "POST",
                                  data,
                                  headers=headers)




            logging.info('groupTagKeyIdStr: %s' %request.groupTagKeyIdStr)

            if request.groupTagKeyIdStr:
                group_user = groupUserController.get_by_groupKeyId_userKeyId(int(request.groupTagKeyIdStr), authorized_user.key.id())
                if group_user:
                    group = groupController.get_by_key_id(int(request.groupTagKeyIdStr))
                    if group:
                        authorized_user.groupTag = "[%s]" % group.tag
                        authorized_user.groupTagKeyId = group.key.id()

            ## try to get the appengine provided geo information
            logging.info(self.request_state)
            try:
                city = self.request_state.headers['x-appengine-city']
            except:
                city = None

            try:
                citylatlon = self.request_state.headers['x-appengine-citylatlong']
            except:
                citylatlon = None

            try:
                country = self.request_state.headers['x-appengine-country']
            except:
                country = None

            try:
                georegion = self.request_state.headers['x-appengine-region']
            except:
                georegion = None

            authorized_user.city = city
            authorized_user.citylatlon = citylatlon
            authorized_user.country = country
            authorized_user.georegion = georegion

            usersController.update(authorized_user)

            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)



            return UserResponse(response_message="Success.", response_successful=True)

        else:

            ## check permissions for admin edit
            if not authorized_user.admin:
                return UserResponse(response_message='Error: Assigned role does not permit this action', response_successful=False)

            entity = usersController.get_by_key_id(int(request.key_id))

            entity.title  = request.title
            entity.description = request.description
            #entity.googleUser = request.googleUser
            #entity.currencyBalance = request.currencyBalance
            entity.region = request.region

            usersController.update(entity)

            response = UserResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                response_message='Success.',
                response_successful=True
            )

            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': entity.key.id()}, countdown = 2,)



            return response


    @endpoints.method(USER_COLLECTION_PAGE_RESOURCE, UserCollection, path='userCollectionGet', http_method='POST', name='collection.get')
    def userCollectionGet(self, request):
        """ Get a collection of users """
        logging.info("userCollectionGet")

        uController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return UserCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('admin is required')
            return UserCollection(response_message='Error: admin is required', response_successful=False)

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        entities, cursor, more  = uController.list_page(start_cursor=curs)
        entity_list = []

        for entity in entities:
            entity_list.append(UserResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description
            ))

        response = UserCollection(
            users = entity_list,
            response_message='Success.  User list returned.',
            response_successful=True
        )

        return response

    @endpoints.method(message_types.VoidMessage, ClientConnectResponse, path='exposeToken', http_method='POST', name='expose.token')
    def exposeToken(self, request):
        """ these tokens are for game servers to request limited user information. """

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
        else:
            response = ClientConnectResponse(
                user_id = claims['user_id'],
                refresh_token = False,
                response_message='Connected successfully.',
                response_successful=True
            )

            usersController = UsersController()
            ultController = UserLoginTokensController()

            ## get this user token or create if needed
            authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('no user record found')
                return ClientConnectResponse(response_message='Error: No User Record Found. ', response_successful=False)


            user_login_token = ultController.get_by_userKeyId(authorized_user.key.id())


            #access_token = ultController.create_unique_access_token()
            access_token = id_token
            logging.info('access_token: %s' %access_token)
            custom_title = "ue4topia.appspot.com/api/v1/login/redirect?access_token=" + access_token

            if not user_login_token:
                logging.info('no existing token found - creating a new one')
                user_login_token = ultController.create(
                userKeyId = authorized_user.key.id(),
                access_token = access_token
                )
                return ClientConnectResponse(response_message='Success. Token Exposed ',
                                            response_successful=True,
                                            custom_title=custom_title,
                                            agreed_with_terms = authorized_user.agreed_with_terms,
                                            access_token=access_token)
            else:
                logging.info('found existing token record - updating it.')
                ## update existing
                user_login_token.access_token = access_token
                ultController.update(user_login_token)

                return ClientConnectResponse(response_message='Success. Token Exposed ',
                                                response_successful=True,
                                                custom_title=custom_title,
                                                agreed_with_terms = authorized_user.agreed_with_terms,
                                                access_token=access_token)

        return response

    @endpoints.method(USER_RESOURCE, ClientConnectResponse, path='referral', http_method='POST', name='referral')
    def referral(self, request):
        """ Give a bonus to users that refer other players. - PROTECTED """

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                response_message='Firebase Unauth.',
                response_successful=False
            )
        else:
            usersController = UsersController()

            ## get this user
            authorized_user = usersController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('no user record found')
                return ClientConnectResponse(response_message='Error: No User Record Found. ', response_successful=False)

            if authorized_user.referral_processed:
                logging.info('referral_processed is already true')
                return ClientConnectResponse(response_message='Error: Referral on this account has already been processed. ', response_successful=False)

            ## ONLY allow this from authorized domains
            request_origin = self.request_state.headers['origin']
            logging.info("request_origin: %s" %request_origin)
            if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
                logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
                return ClientConnectResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)




            ## get the referral user
            referral_user = usersController.get_by_key_id(int(request.key_id))
            if not referral_user:
                logging.info('the referral_user was not found')
                return ClientConnectResponse(response_message='Error: The referral user was not found. ', response_successful=False)

            ## make sure they are different users!
            if referral_user.key.id() == authorized_user.key.id():
                logging.info('the referral_user was the same as the authorized user')
                return ClientConnectResponse(response_message='Error: You cannot give the referral bonus to yourself. ', response_successful=False)

            ## create a transaction + alert for the referral user
            ## FREE MONEY!!!!
            description = "Thanks for the referral!"

            ## Create a transaction for the deposit -user
            transaction = TransactionsController().create(
                userKeyId = referral_user.key.id(),
                firebaseUser = referral_user.firebaseUser,
                description = description,
                ##confirmations = 0,
                amountInt = CRED_BONUS_REFERRAL,
                #serverKeyId = server.key.id(),
                #serverTitle = server.title,
                ##amount = currency_hold / 100000000. * -1,
                #newBalanceInt = authorized_user.currencyBalance,
                #newBalance = float(authorized_user.currencyBalance) / 100000000.
                transactionType = "user",
                transactionClass = "referral",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_REFERRAL,
                materialDisplayClass = "md-primary"
                )

            if BONUS_REFERRALS_ENABLED:
                logging.info('bonus referrals are enabled')

                BONUS_CRED_BONUS_REFERRAL = int(CRED_BONUS_REFERRAL / 2)

                description = "Bonus referral."

                transaction = TransactionsController().create(
                    userKeyId = referral_user.key.id(),
                    firebaseUser = referral_user.firebaseUser,
                    description = description,
                    ##confirmations = 0,
                    amountInt = BONUS_CRED_BONUS_REFERRAL,
                    #serverKeyId = server.key.id(),
                    #serverTitle = server.title,
                    ##amount = currency_hold / 100000000. * -1,
                    #newBalanceInt = authorized_user.currencyBalance,
                    #newBalance = float(authorized_user.currencyBalance) / 100000000.
                    transactionType = "user",
                    transactionClass = "referral",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_REFERRAL,
                    materialDisplayClass = "md-primary"
                    )

            lockController = TransactionLockController()

            pushable = lockController.pushable("user:%s"%referral_user.key.id())
            if pushable:
                logging.info('referral_user pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": referral_user.key.id()
                                                                                }, countdown=2)

            ## push an alert out to firebase
            taskUrl='/task/user/alert/create'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': referral_user.firebaseUser,
                                                                            'material_icon': MATERIAL_ICON_REFERRAL,
                                                                            'importance': 'md-primary',
                                                                            ## TODO this message can be more helpful
                                                                            'message_text': description,
                                                                            'action_button_color': 'primary',
                                                                            'action_button_sref': '#/user/transactions'
                                                                            }, countdown = 10,)
            ## create a freind request?
            ## We'll do this in JS instead and use the actual friend endpoint.

            ## update the authorized user
            authorized_user.referral_processed = True
            authorized_user.referred_by = referral_user.key.id()
            usersController.update(authorized_user)

            response = ClientConnectResponse(
                response_message='Referral Processed.',
                response_successful=True
            )

        return response


    @endpoints.method(USER_RESOURCE, UserResponse, path='postLoginProcess', http_method='POST', name='postLoginProcess')
    def postLoginProcess(self, request):
        """ Specific processing which occurs after a user has logged in using a UE game client """
        logging.info("postLoginProcess")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
        else:

            matchPlayerController = MatchPlayersController()
            usersController = UsersController()

            ## get this user
            authorized_user = usersController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('no user record found')
                return UserResponse(response_message='Error: No User Record Found. ', response_successful=False)


            ## check to see if the user has any matches that they should auto-rejoin
            joinable_match_player = matchPlayerController.get_joinable_by_gameKeyId_userKeyId(int(request.gameKeyIdStr), authorized_user.key.id() )
            if joinable_match_player:
                logging.info('found a joinable match ')

                ## TODO check to see if this is stale - fix and remove the database record if it is
                # get the match
                match = MatchController().get_by_key_id(joinable_match_player.matchKeyId)
                if match:
                    logging.info('found a match')
                    ## TODO any other checks on the match?

                    ## tell the client that matchmaker has started.
                    ## Push a notification out through the socket server
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())
                    headers = {"Content-Type": "application/json"}

                    push_payload = {'matchType': match.gameModeTitle}

                    payload_json = json.dumps(push_payload)

                    #try:
                    URL = "%s/user/%s/matchmaker/started" % (HEROKU_SOCKETIO_SERVER, joinable_match_player.firebaseUser)
                    resp, content = http_auth.request(URL,
                                            ##"PATCH",
                                          "PUT", ## Write or replace data to a defined path,
                                          payload_json,
                                          headers=headers)

                    logging.info(resp)
                    logging.info(content)

                    chat_message = "You have an active match.  Sending you there now."

                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': joinable_match_player.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })


                    ## in a few seconds, send the user to the match.

                    match_data = {'key_id': joinable_match_player.matchKeyId,
                                    'matchmakerStarted': joinable_match_player.matchmakerStarted,
                                    'matchmakerPending': joinable_match_player.matchmakerPending,
                                    'matchmakerFoundMatch': joinable_match_player.matchmakerFoundMatch,
                                    'matchmakerFinished': joinable_match_player.matchmakerFinished,
                                    'matchmakerServerReady': joinable_match_player.matchmakerServerReady,
                                    'matchmakerJoinable': joinable_match_player.matchmakerJoinable,
                                    'session_host_address': match.hostConnectionLink or "",
                                    'matchType': match.gameModeTitle,
                                    'session_id': match.session_id or ""
                                    }

                    match_json = json.dumps(match_data)

                    ## TODO send them a chat message too

                    ## moving matchmaker complete to a task

                    taskUrl='/task/game/match/matchmaker_complete'
                    taskqueue.add(url=taskUrl, queue_name='matchmakerPush', params={'firebaseUser': authorized_user.firebaseUser,
                                                                                    'match_json': match_json
                                                                                    }, countdown = 5)


            return UserResponse(response_message='Success. ', response_successful=True)


    @endpoints.method(USER_RESOURCE, UserResponse, path='refreshToken', http_method='POST', name='refreshToken')
    def refreshToken(self, request):
        """ Refresh user token """
        logging.info("refreshToken")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        except:
            logging.error('auth claims not verified - likely an expired token')
            ## TODO log the error or something
            claims = None

        if not claims:
            logging.error('Firebase Unauth')
            response = UserResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
        else:

            usersController = UsersController()
            matchPlayersController = MatchPlayersController()
            gameController = GamesController()

            ## get this user
            authorized_user = usersController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('no user record found')
                return UserResponse(response_message='Error: No User Record Found. ', response_successful=False)

            if not authorized_user.refreshToken:
                logging.info('no refreshToken found')
                return UserResponse(response_message='Error: No refreshToken Found. ', response_successful=False)

            FIREBASE_SCOPES = [
                'https://www.googleapis.com/auth/firebase.database',
                #'https://www.googleapis.com/auth/firebase.readonly',
                #'https://www.googleapis.com/auth/cloud-platform',
                #'https://www.googleapis.com/auth/firebase',
                'https://www.googleapis.com/auth/securetoken',
                'https://www.googleapis.com/auth/userinfo.email']

            #credentials = GoogleCredentials.get_application_default().create_scoped(FIREBASE_SCOPES)
            credentials = AppAssertionCredentials(FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            push_payload = {"refresh_token": authorized_user.refreshToken, "grant_type": "refresh_token"}

            payload_json = json.dumps(push_payload)

            #try:
            URL = "https://securetoken.googleapis.com/v1/token?key=%s" % (GOOGLE_SERVER_API_KEY)
            resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "POST", ## Write or replace data to a defined path,
                                  payload_json,
                                  headers=headers)

            logging.info(resp)
            logging.info(content)

            json_response = json.loads(content)

            logging.info(json_response['access_token'])
            logging.info(json_response['refresh_token'])

            ## storing this in the user model for now
            ## TODO move this to user login tokens, just in case.



            users_join_pending_match_player = matchPlayersController.get_join_pending_by_userKeyId(authorized_user.key.id())
            if users_join_pending_match_player:
                logging.info('found a join pending match player.  updating it so it does not get removed by the cron job')

                ## update any active match player so it does not expire.
                game = gameController.get_by_key_id(users_join_pending_match_player.gameKeyId)
                if game:
                    ## calculate or create a stale timestamp from game max timeout
                    ## this needs to be longer than the max timeout to ensure that the match is cancelled before the match player
                    if game.match_timeout_max_minutes:
                        timeout_duration_seconds = (game.match_timeout_max_minutes + 40) * 60
                    else:
                        timeout_duration_seconds = 100 * 60

                    users_join_pending_match_player.stale = datetime.datetime.now() + datetime.timedelta(seconds=timeout_duration_seconds)
                    matchPlayersController.update(users_join_pending_match_player)

            if authorized_user.twitch_streamer:
                twitch_changed = False

                logging.info('twitch streamer found - checking stream status')
                headers = {"Content-Type": "application/json", "Client-ID": TWITCH_CLIENT_ID}
                URL = "https://api.twitch.tv/kraken/streams/%s" % authorized_user.twitch_channel_id

                try:
                    resp, content = http_auth.request(URL,
                                        "GET",
                                      ##"PUT", ## Write or replace data to a defined path,
                                      #user_json,
                                      headers=headers)

                    #logging.info(resp)
                    logging.info(content)
                    stream_info_json = json.loads(content)
                    if stream_info_json['stream']:
                        logging.info('stream info found')
                        if not authorized_user.twitch_currently_streaming:
                            twitch_changed = True
                        authorized_user.twitch_currently_streaming = True
                        authorized_user.twitch_stream_game = stream_info_json['stream']['game']
                        authorized_user.twitch_stream_viewers = stream_info_json['stream']['viewers']
                    else:
                        if authorized_user.twitch_currently_streaming:
                            twitch_changed = True
                        authorized_user.twitch_currently_streaming = False
                except:
                    if authorized_user.twitch_currently_streaming:
                        twitch_changed = True
                    authorized_user.twitch_currently_streaming = False
                    authorized_user.twitch_stream_game = ""
                    authorized_user.twitch_stream_viewers = 0

                if twitch_changed:
                    logging.info('twitch status changed')
                    usersController.update(authorized_user)


            return UserResponse(accessToken=json_response['access_token'])
