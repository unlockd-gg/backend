import endpoints
import logging
import uuid
import urllib
import json
import datetime
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

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.models.groups import *
from apps.uetopia.models.group_users import *
from apps.uetopia.models.group_roles import *
from apps.uetopia.models.group_games import *

from apps.uetopia.controllers.games import GamesController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="groups", version="v1", description="Groups API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class GroupsApi(remote.Service):
    @endpoints.method(GROUP_CREATE_RESOURCE, GroupResponse, path='create', http_method='POST', name='create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def create(self, request):
        """ Create a new group """
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        ## check if a group already exists owned by this player
        existing_group = groupsController.get_by_ownerPlayerKeyId(authorized_user.key.id())

        if existing_group:
            return GroupResponse(response_message='Error: You can only own a single group.  Resign leadership, or delete your other group',
                                    response_successful=False
                                )

        ## check the tag
        existing_group_tag = groupsController.get_by_tag(request.tag)

        if existing_group_tag:
            return GroupResponse(response_message='Error: The requested tag already exists.  Please use another.',
                                    response_successful=False )

        if GROUP_TAG_MINIMUM_STR_SIZE > len(request.tag):
            return GroupResponse(response_message='Error: The requested tag is too short.  Minimum size is: %s'%GROUP_TAG_MINIMUM_STR_SIZE,
                                    response_successful=False )

        if GROUP_TAG_MAXIMUM_STR_SIZE < len(request.tag):
            return GroupResponse(response_message='Error: The requested tag is too long.  Maximum size is: %s'%GROUP_TAG_MAXIMUM_STR_SIZE,
                                    response_successful=False )

        banner_base_url = "/img/groups/"
        if request.genre == "Clan":
            banner_url = banner_base_url + "default_red.png"
        elif request.genre == "Community":
            banner_url = banner_base_url + "default_purple.png"
        elif request.genre == "eSports":
            banner_url = banner_base_url + "default_yellow.png"
        else:
            banner_url = banner_base_url + "default_blue.png"

        group = groupsController.create(
            ownerPlayerKeyId = authorized_user.key.id(),
            ##slugifyUrl = request.slugifyUrl,
            #invisible = request.invisible,
            #iconServingUrl = request.iconServingUrl,
            bannerServingUrl = banner_url,
            #cssServingUrl = request.cssServingUrl,
            title = request.title,
            description = request.description,
            genre = request.genre,
            #website = request.website,
            tag = request.tag,
            recruiting = request.recruiting,
            recruiting_poilicy = request.recruiting_poilicy,
            application_message = request.application_message,
            currencyBalance = 0
        )

        ## add default roles
        owner_role = groupRolesController.create(
            groupKeyId = group.key.id(),
            groupTitle = group.title,
            title = "Leader",
            update_group_settings = True,
            update_group_roles = True,
            update_player_roles = True,
            create_events = True,
            update_events = True,
            update_games = True,
            update_servers = True,
            create_matches = True,
            create_tournaments = True,
            sponsor_tournaments = True,
            create_ads = True,
            edit_ads = True,
            view_transactions = True,
            chat_membership = True,
            applicant_role = False,
            leader_role = True,
            order = 1,
            join_group_servers = True,
            join_group_server_instances = True,
            join_group_tournaments = True,
            drop_items_in_group_servers = True,
            pickup_items_in_group_servers = True,
            donate_to_members = True,
            metagame_faction_lead = True,
            metagame_team_lead = True,
            raid_lead = True,
        )
        member_role = groupRolesController.create(
            groupKeyId = group.key.id(),
            groupTitle = group.title,
            title = "Member",
            update_group_settings = False,
            update_group_roles = False,
            update_player_roles = False,
            create_events = False,
            update_events = False,
            update_games = False,
            update_servers = False,
            create_matches = True,
            chat_membership = True,
            create_tournaments = False,
            sponsor_tournaments = False,
            create_ads = False,
            edit_ads = False,
            view_transactions = False,
            applicant_role = False,
            leader_role = False,
            order = 2,
            join_group_servers = True,
            join_group_server_instances = True,
            join_group_tournaments = True,
            drop_items_in_group_servers = True,
            pickup_items_in_group_servers = False,
            donate_to_members = False,
            metagame_faction_lead = False,
            metagame_team_lead = True,
            raid_lead = False
        )
        applicant_role = groupRolesController.create(
            groupKeyId = group.key.id(),
            groupTitle = group.title,
            title = "Applicant",
            update_group_settings = False,
            update_group_roles = False,
            update_player_roles = False,
            create_events = False,
            update_events = False,
            update_games = False,
            update_servers = False,
            create_matches = False,
            create_tournaments = False,
            sponsor_tournaments = False,
            create_ads = False,
            edit_ads = False,
            view_transactions = False,
            chat_membership = False,
            applicant_role = True,
            leader_role = False,
            order = 3,
            join_group_servers = False,
            join_group_server_instances = False,
            join_group_tournaments = False,
            drop_items_in_group_servers = False,
            pickup_items_in_group_servers = False,
            donate_to_members = False,
            metagame_faction_lead = False,
            metagame_team_lead = False,
            raid_lead = False
        )

        ## add the owner as leader
        group_user = groupUsersController.create(
            groupKeyId = group.key.id(),
            groupTitle = group.title,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            firebaseUser = authorized_user.firebaseUser,
            picture = authorized_user.picture,
            order = 1,
            role_title = "Leader",
            roleKeyId = owner_role.key.id(),
            #vettingEnabled = True,
            #vettingCompleted = False,
            #vettingFinalized = False,
            #gkpAmount = 0.0,
            #gkpVettingRemaining = 4
        )

        ## create the chat channel for this group
        group_chat_title = group.title + " chat"
        chat_channel = ChatChannelsController().create(
            title = group_chat_title,
            #text_enabled = True,
            #data_enabled = False,
            channel_type = 'group',
            adminUserKeyId = authorized_user.key.id(),
            refKeyId = group.key.id(),
            max_subscribers = 200
        )
        ## Subscribe the player to it
        subscriber = ChatChannelSubscribersController().create(
            online = True,
            chatChannelKeyId = chat_channel.key.id(),
            chatChannelTitle = chat_channel.title,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            userFirebaseUser = authorized_user.firebaseUser,
            post_count = 0,
            chatChannelRefKeyId = group.key.id(),
            channel_type = 'group',
            chatChannelOwnerKeyId = authorized_user.key.id()
        )

        chat_message = "> Chat Channel %s created" % request.title

        taskUrl='/task/chat/channel/list_changed'
        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                        'userKeyId': authorized_user.key.id(),
                                                                        'textMessage': chat_message
                                                                        }, countdown = 2)

        taskUrl='/task/chat/send'
        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                            "message": chat_message,
                                                                            "created":datetime.datetime.now().isoformat()
                                                                        })

        taskUrl='/task/group/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': group.key.id()}, countdown = 2,)

        taskUrl='/task/group/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': group_user.key.id()}, countdown = 4,)

        return GroupResponse(response_message='Success.  Group Created. ', response_successful=True)

    @endpoints.method(GROUP_EDIT_RESOURCE, GroupResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a group """
        logging.info("groupGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        if not request.key_id:
            return GamesResponse(response_message="key_id is required")

        entity = groupsController.get_by_key_id(int(request.key_id))

        if authorized_user.key.id() == entity.ownerPlayerKeyId:
            logging.info('owner found')
            response = GroupResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                genre = entity.genre,
                tag = entity.tag,

                website = entity.website,
                iconServingUrl = entity.iconServingUrl,
                bannerServingUrl = entity.bannerServingUrl,

                currencyBalance = entity.currencyBalance,
                recruiting = entity.recruiting,
                recruiting_poilicy = entity.recruiting_poilicy,
                application_message = entity.application_message,

                slack_webhook = entity.slack_webhook,
                slack_subscribe_errors = entity.slack_subscribe_errors,
                slack_subscribe_transactions = entity.slack_subscribe_transactions,
                slack_subscribe_config_changes = entity.slack_subscribe_config_changes,
                slack_subscribe_new_users = entity.slack_subscribe_new_users,
                slack_subscribe_tournaments = entity.slack_subscribe_tournaments,

                discord_webhook = entity.discord_webhook,
                discord_subscribe_errors = entity.discord_subscribe_errors,
                discord_subscribe_transactions = entity.discord_subscribe_transactions,
                discord_subscribe_config_changes = entity.discord_subscribe_config_changes,
                discord_subscribe_new_users = entity.discord_subscribe_new_users,
                discord_subscribe_tournaments = entity.discord_subscribe_tournaments,

                discord_subscribe_group_event_feeds = entity.discord_subscribe_group_event_feeds,
                discord_subscribe_game_event_feeds = entity.discord_subscribe_game_event_feeds,
                discord_subscribe_consignments = entity.discord_subscribe_consignments,

                #inGameTextureServingUrl = entity.inGameTextureServingUrl,

                response_message='Success.',
                response_successful=True
            )
        else:
            ## send only the public data
            ## public data is normally served via firebase, so this is only in case a user tries to load from the endpoint using thier credentials.
            response = GroupResponse(
                key_id = entity.key.id(),
                title = entity.title,
                description = entity.description,
                response_message='Success.',
                response_successful=True
            )

        return response

    @endpoints.method(GROUP_EDIT_RESOURCE, GroupResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update a group """
        logging.info("groupUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        if not request.key_id:
            return GroupResponse(response_message="key_id is required", response_successful=False)

        entity = groupsController.get_by_key_id(int(request.key_id))

        if not entity:
            logging.error("Error: No group found with the supplied key_id")
            return GroupResponse(response_message="Error: No group found with the supplied key_id", response_successful=False)


        ## TODO - Use the role/permission here instead.
        if authorized_user.key.id() == entity.ownerPlayerKeyId:
            logging.info('owner found')

            logging.info(request.title)
            logging.info(request.description)

            entity.title = request.title
            entity.description = request.description
            entity.genre = request.genre

            entity.website = request.website

            entity.recruiting = request.recruiting
            entity.recruiting_poilicy = request.recruiting_poilicy
            entity.application_message = request.application_message

            ## TODO deal with tag

            entity.iconServingUrl = request.iconServingUrl
            entity.bannerServingUrl = request.bannerServingUrl

            entity.slack_webhook = request.slack_webhook
            entity.slack_subscribe_errors = request.slack_subscribe_errors
            entity.slack_subscribe_transactions = request.slack_subscribe_transactions
            entity.slack_subscribe_config_changes = request.slack_subscribe_config_changes
            entity.slack_subscribe_new_users = request.slack_subscribe_new_users
            entity.slack_subscribe_tournaments = request.slack_subscribe_tournaments

            entity.discord_webhook = request.discord_webhook
            entity.discord_subscribe_errors = request.discord_subscribe_errors
            entity.discord_subscribe_transactions = request.discord_subscribe_transactions
            entity.discord_subscribe_config_changes = request.discord_subscribe_config_changes
            entity.discord_subscribe_new_users = request.discord_subscribe_new_users
            entity.discord_subscribe_tournaments  = request.discord_subscribe_tournaments

            entity.discord_subscribe_group_event_feeds = request.discord_subscribe_group_event_feeds
            entity.discord_subscribe_game_event_feeds = request.discord_subscribe_game_event_feeds
            entity.discord_subscribe_consignments = request.discord_subscribe_consignments

            #entity.inGameTextureServingUrl = request.inGameTextureServingUrl

        groupsController.update(entity)

        taskUrl='/task/group/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': entity.key.id()}, countdown = 2,)

        try:
            name = claims['name']
        except:
            name = claims['email']

        ## do slack/discord pushes if enabled
        if entity.slack_subscribe_config_changes and entity.slack_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Configuration Changed by: %s | %s" % (name, claims['email'])
            slack_data = {'text': message}
            data=json.dumps(slack_data)
            resp, content = http_auth.request(entity.slack_webhook,
                              "POST",
                              data,
                              headers=headers)

        if entity.discord_subscribe_config_changes:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Configuration Changed by: %s | %s" % (name, claims['email'])
            discord_data = { "embeds": [{"title": "Configuration Changed", "url": "https://example.com", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(entity.discord_webhook,
                              "POST",
                              data,
                              headers=headers)

        response = GroupResponse(
            key_id = entity.key.id(),
            title = entity.title,
            description = entity.description,
            genre = entity.genre,
            response_message='Success.  Group updated.',
            response_successful=True
        )

        return response

    @endpoints.method(GROUP_COLLECTION_PAGE_RESOURCE, GroupCollection, path='groupCollectionGetPage', http_method='POST', name='collection.get.page')
    def groupCollectionGetPage(self, request):
        """ Get a collection of groups """
        logging.info("groupCollectionGetPage")

        ## no auth is required.

        gcontroller = GroupsController()

        curs = Cursor(urlsafe=request.cursor)
        sort_order = request.sort_order
        direction = request.direction

        groups, cursor, more = gcontroller.list_visible_page(start_cursor=curs, order=sort_order)
        grouplist = []

        for group in groups:
            grouplist.append(GroupResponse(
                key_id = group.key.id(),
                invisible = group.invisible,
                iconServingUrl = group.iconServingUrl,
                bannerServingUrl = group.bannerServingUrl,
                cssServingUrl = group.cssServingUrl,
                title = group.title,
                description = group.description,
                genre = group.genre,
                website = group.website,
                tag = group.tag,
                recruiting = group.recruiting,
                recruiting_poilicy = group.recruiting_poilicy,
            ))

        if cursor:
            cursor_url = cursor.urlsafe()
        else:
            cursor_url = None

        response = GroupCollection(
            groups = grouplist,
            more = more,
            cursor = cursor_url,
            #sort_order = sort_order,
            #direction = direction
        )

        return response

    ## GROUP MEMBERS

    @endpoints.method(GROUP_GET_RESOURCE, GroupResponse, path='groupJoin', http_method='POST', name='join')
    def groupJoin(self, request):
        """ Apply to join a group """
        logging.info("groupJoin")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        if not request.key_id:
            return GroupResponse(response_message="key_id is required", response_successful=False)

        ## get the group
        group = groupsController.get_by_key_id(int(request.key_id))
        if not group:
            return GroupResponse(response_message='Error: Could not find a group with the supplied key.')

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.key_id, authorized_user.key.id())

        if not group_member:
            ## get the applicant role
            applicant_role = groupRolesController.get_by_groupKeyId_applicant_role(request.key_id)

            if applicant_role:
                group_member = groupUsersController.create(
                    groupKeyId = group.key.id(),
                    groupTitle = group.title,
                    userKeyId = authorized_user.key.id(),
                    userTitle = authorized_user.title,
                    firebaseUser = authorized_user.firebaseUser,
                    picture = authorized_user.picture,
                    applicant = True,
                    approved = False,
                    order = applicant_role.order,
                    role_title = applicant_role.title,
                    roleKeyId = applicant_role.key.id(),
                    application_message = request.application_message,
                    #vettingEnabled = True,
                    #vettingCompleted = False,
                    #vettingFinalized = False,
                    #gkpAmount = 0.0,
                    #gkpVettingRemaining = 4
                )

                taskUrl='/task/group/user/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': group_member.key.id()}, countdown = 4,)

                ## give this user an alert too so they know the application has been received
                ## push an alert out to firebase
                taskUrl='/task/user/alert/create'
                action_link = '#/groups/' + str(group.key.id())
                message_text = "You have applied to join %s" % group.title
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': authorized_user.firebaseUser,
                                                                                'material_icon': MATERIAL_ICON_GROUP,
                                                                                'importance': 'md-primary',
                                                                                ## TODO this message can be more helpful
                                                                                'message_text': message_text,
                                                                                'action_button_color': 'primary',
                                                                                'action_button_sref': action_link
                                                                                }, countdown = 0,)

                ##  if applicant role has chat permissions, subscribe them to the chat channel
                if applicant_role.chat_membership:
                    logging.info('applicant role can chat.')

                    ## get the group chat channel
                    group_chat_channel = ChatChannelsController().get_by_channel_type_refKeyId("group", group.key.id())

                    ## Subscribe the player to it
                    subscriber = ChatChannelSubscribersController().create(
                        online = True,
                        chatChannelKeyId = group_chat_channel.key.id(),
                        chatChannelTitle = group_chat_channel.title,
                        userKeyId = authorized_user.key.id(),
                        userTitle = authorized_user.title,
                        userFirebaseUser = authorized_user.firebaseUser,
                        post_count = 0,
                        chatChannelRefKeyId = group.key.id(),
                        channel_type = 'group',
                        chatChannelOwnerKeyId = authorized_user.key.id()
                    )

                    chat_message = "> Chat Channel %s joined" % request.title

                    taskUrl='/task/chat/channel/list_changed'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                                    'userKeyId': authorized_user.key.id(),
                                                                                    'textMessage': chat_message
                                                                                    }, countdown = 2)

                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })



                ## send messaging out if configured
                if group.discord_subscribe_new_users and group.discord_webhook:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/groups/%s/users/%s" % (group.key.id(), authorized_user.key.id())
                    message = "%s  %s" % (authorized_user.title, link)
                    #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                    discord_data = { "embeds": [{"title": "New Group Join Application", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                if group.slack_subscribe_new_users:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/groups/%s/users/%s" % (group.key.id(), authorized_user.key.id())
                    message = "New Group Join Application: %s | %s" % (link, authorized_user.title)
                    slack_data = {'text': message}
                    data=json.dumps(slack_data)
                    resp, content = http_auth.request(group.slack_webhook,
                                      "POST",
                                      data,
                                      headers=headers)

                ## TODO Sense


                return GroupResponse(response_message='Success.', response_successful=True)
        else:
            logging.info('You are already a member of this group.')
            return GroupResponse(response_message='Error: You are already a member of this group.', response_successful=False)

    @endpoints.method(GROUP_GET_RESOURCE, GroupUserResponse, path='groupUserGet', http_method='POST', name='user.get')
    def groupUserGet(self, request):
        """ Get a group user """
        logging.info("groupUserGet")

        ## this is the method all users call when loading the groups page, to check if they are members.

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupUserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.key_id, authorized_user.key.id())

        if not group_member:
            return GroupUserResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            return GroupUserResponse(response_message='Error: Role not found.', response_successful=False)


        return GroupUserResponse(response_message='Success.',
                                response_successful=True,
                                key_id = group_member.key.id(),
                                userKeyId = group_member.userKeyId,
                                userTitle = group_member.userTitle,
                                role_title = group_member.role_title,
                                roleKeyId = group_member.roleKeyId,
                                update_group_settings = group_member_role.update_group_settings,
                                update_group_roles = group_member_role.update_group_roles,
                                update_player_roles = group_member_role.update_player_roles,
                                create_events = group_member_role.create_events,
                                update_events = group_member_role.update_events,
                                update_games = group_member_role.update_games,
                                update_servers = group_member_role.update_servers,
                                create_matches = group_member_role.create_matches,
                                create_tournaments = group_member_role.create_tournaments,
                                sponsor_tournaments = group_member_role.sponsor_tournaments,
                                create_ads = group_member_role.create_ads,
                                edit_ads = group_member_role.edit_ads,
                                view_transactions = group_member_role.view_transactions,
                                chat_membership = group_member_role.chat_membership,
                                applicant = group_member.applicant,
                                approved = group_member.approved,
                                application_message = group_member.application_message,
                                #member = True
                                )

    @endpoints.method(GROUP_USER_RESOURCE, GroupUserCollection, path='groupMemberCollection', http_method='POST', name='member.collection')
    def groupMemberCollection(self, request):
        """ Get a collection of group users """
        logging.info("groupMemberCollection")

        ## this is the call group admins make when fetching users for editing

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupUserCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupUserResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupUserResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        group_membership_results = groupUsersController.get_list_by_userKeyId(authorized_user.key.id())

        results_list = []

        for group_member in group_membership_results:
            results_list.append(GroupUserResponse(
                                        response_message='Success.',
                                        response_successful=True,
                                        key_id = group_member.key.id(),
                                        userKeyId = group_member.userKeyId,
                                        userTitle = group_member.userTitle,
                                        role_title = group_member.role_title,
                                        roleKeyId = group_member.roleKeyId,
                                        groupKeyId = group_member.groupKeyId,
                                        groupTitle = group_member.groupTitle
            ))

        response = GroupUserCollection(
            group_users = results_list,
            #more = more,
            #cursor = cursor_url,
            #sort_order = sort_order,
            #direction = direction
        )

        return response


    @endpoints.method(GROUP_USER_RESOURCE, GroupUserResponse, path='groupMemberGet', http_method='POST', name='member.get')
    def groupMemberGet(self, request):
        """ Get a group member """
        logging.info("groupMemberGet")

        ## this is the call group admins make when fetching users for editing

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupUserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupUserResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupUserResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        ## check if the authenticated user is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if not group_member:
            return GroupUserResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            return GroupUserResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_player_roles:
            return GroupUserResponse(response_message='Error: You do not have sufficient permissions to update roles for this user.', response_successful=False)

        ## get the requested group user
        requested_group_member = groupUsersController.get_by_key_id(int(request.key_id))
        if not requested_group_member:
            return GroupUserResponse(response_message='Error: Member not found', response_successful=False)

        return GroupUserResponse(response_message='Success.',
                                key_id = requested_group_member.key.id(),
                                userKeyId = requested_group_member.userKeyId,
                                userTitle = requested_group_member.userTitle,
                                role_title = requested_group_member.role_title,
                                roleKeyId = requested_group_member.roleKeyId,
                                applicant = requested_group_member.applicant,
                                approved = requested_group_member.approved,
                                order = requested_group_member.order,
                                application_message = requested_group_member.application_message,
                                response_successful = True
                                )


    @endpoints.method(GROUP_USER_RESOURCE, GroupUserResponse, path='groupMemberupdate', http_method='POST', name='member.update')
    def groupMemberUpdate(self, request):
        """ Update a group member """
        logging.info("groupMemberUpdate")

        ## this is the call group admins make when updating users

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupUserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupUserResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupUserResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        chatSubscriberController = ChatChannelSubscribersController()

        ## check if the authenticated user is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if not group_member:
            return GroupUserResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            return GroupUserResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_player_roles:
            return GroupUserResponse(response_message='Error: You do not have sufficient permissions to update roles for this user.', response_successful=False)

        ## get the requested group user
        requested_group_member = groupUsersController.get_by_key_id(request.key_id)
        if not requested_group_member:
            return GroupUserResponse(response_message='Error: Member not found', response_successful=False)

        ## get the group
        group = groupsController.get_by_key_id(requested_group_member.groupKeyId)
        if not group:
            return GroupResponse(response_message='Error: Could not find a group with the supplied key.')

        ## get the previous role
        requested_group_member_previous_role = groupRolesController.get_by_key_id(requested_group_member.roleKeyId)
        if not requested_group_member_previous_role:
            return GroupUserResponse(response_message='Error: Previous Role not found.', response_successful=False)

        ## get the new role
        requested_group_member_role = groupRolesController.get_by_key_id(request.roleKeyId)
        if not requested_group_member_role:
            return GroupUserResponse(response_message='Error: Role not found.', response_successful=False)

        ## deal with chat subscriber if it has changed.
        if requested_group_member_previous_role.chat_membership != requested_group_member_role.chat_membership:
            logging.info('chat membership permission has changed!!!')
            ## in either case, we need the channel and any existing subscriber
            ## get the group chat channel
            group_chat_channel = ChatChannelsController().get_by_channel_type_refKeyId("group", group.key.id())
            ## get the subscriber
            existing_chat_subscriber = chatSubscriberController.get_by_channel_and_user(group_chat_channel.key.id(), requested_group_member.userKeyId)

            if requested_group_member_role.chat_membership:
                logging.info('adding the chat subscriber')
                ## make sure it does not exist first
                if not existing_chat_subscriber:
                    logging.info('no existing subscriber found - creating one')
                    existing_chat_subscriber = chatSubscriberController.create(
                        online = True,
                        chatChannelKeyId = group_chat_channel.key.id(),
                        chatChannelTitle = group_chat_channel.title,
                        userKeyId = requested_group_member.userKeyId,
                        userTitle = requested_group_member.userTitle,
                        userFirebaseUser = requested_group_member.firebaseUser,
                        post_count = 0,
                        chatChannelRefKeyId = group.key.id(),
                        channel_type = 'group',
                        chatChannelOwnerKeyId = group_chat_channel.adminUserKeyId
                    )
                chat_message = "> Chat Channel %s joined" % group_chat_channel.title

            else:
                logging.info('deleting the chat subscriber')
                if existing_chat_subscriber:
                    chatSubscriberController.delete(existing_chat_subscriber)

                chat_message = "> Chat Channel %s left" % group_chat_channel.title

            ## notify the user
            taskUrl='/task/chat/channel/list_changed'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': requested_group_member.firebaseUser,
                                                                            'userKeyId': requested_group_member.userKeyId,
                                                                            'textMessage': chat_message
                                                                            }, countdown = 2)

            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': requested_group_member.firebaseUser,
                                                                                "message": chat_message,
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })


        requested_group_member.userTitle = request.userTitle
        requested_group_member.role_title = requested_group_member_role.title
        requested_group_member.roleKeyId = requested_group_member_role.key.id()
        requested_group_member.order = request.order

        ## turn off applicant if it was on.
        if requested_group_member.applicant:
            requested_group_member.applicant = False
            requested_group_member.approved = True

        groupUsersController.update(requested_group_member)

        ## update firebase
        taskUrl='/task/group/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': requested_group_member.key.id()}, countdown = 2,)


        return GroupUserResponse(response_message='Success.',
                                key_id = requested_group_member.key.id(),
                                userKeyId = requested_group_member.userKeyId,
                                userTitle = requested_group_member.userTitle,
                                role_title = requested_group_member.role_title,
                                roleKeyId = requested_group_member.roleKeyId,
                                applicant = requested_group_member.applicant,
                                approved = requested_group_member.approved,
                                order = requested_group_member.order,
                                response_successful = True
                                )

    ## Group Member Remove
    @endpoints.method(GROUP_USER_RESOURCE, GroupUserResponse, path='groupMemberRemove', http_method='POST', name='member.remove')
    def groupMemberRemove(self, request):
        """ Remove a group member """
        logging.info("groupMemberRemove")

        ## this is the call group admins make when removing users

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupUserResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupUserResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupUserResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        chatSubscriberController = ChatChannelSubscribersController()
        userController = UsersController()

        ## check if the authenticated user is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if not group_member:
            return GroupUserResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            return GroupUserResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_player_roles:
            return GroupUserResponse(response_message='Error: You do not have sufficient permissions to update roles for this user.', response_successful=False)

        ## get the requested group user
        requested_group_member = groupUsersController.get_by_key_id(request.key_id)
        if not requested_group_member:
            return GroupUserResponse(response_message='Error: Member not found', response_successful=False)

        ## get the group
        group = groupsController.get_by_key_id(requested_group_member.groupKeyId)
        if not group:
            return GroupResponse(response_message='Error: Could not find a group with the supplied key.')

        requested_group_member_user = userController.get_by_key_id(requested_group_member.userKeyId)

        group_chat_channel = ChatChannelsController().get_by_channel_type_refKeyId("group", group.key.id())
        ## get the subscriber
        existing_chat_subscriber = chatSubscriberController.get_by_channel_and_user(group_chat_channel.key.id(), requested_group_member.userKeyId)

        if existing_chat_subscriber:
            logging.info('deleting the chat subscriber')
            chatSubscriberController.delete(existing_chat_subscriber)

            chat_message = "> Chat Channel %s left" % group_chat_channel.title

            ## notify the user
            taskUrl='/task/chat/channel/list_changed'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': requested_group_member.firebaseUser,
                                                                            'userKeyId': requested_group_member.userKeyId,
                                                                            'textMessage': chat_message
                                                                            }, countdown = 2)

            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': requested_group_member.firebaseUser,
                                                                                "message": chat_message,
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })
        firebaseUser = requested_group_member.firebaseUser
        groupUsersController.delete(requested_group_member)

        ## deleting from firebase too
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        #game_json = json.dumps(game.to_json())
        headers = {"Content-Type": "application/json"}
        URL = "https://ue4topia.firebaseio.com/groups/%s/users/%s.json" % (group.key.id(), firebaseUser)

        ## Reset the user's guild TAG if the user was using this group's TAG
        if requested_group_member_user.groupTagKeyId == group.key.id():
            logging.info('resetting user group tag')
            requested_group_member_user.groupTagKeyId = None
            requested_group_member_user.groupTag = None
            userController.update(requested_group_member_user)

            ## and update the user on firebase
            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': requested_group_member_user.key.id()}, countdown = 2,)


        resp, content = http_auth.request(URL,
                      "DELETE", ## We can delete data with a DELETE request
                      #game_json,
                      headers=headers)


        return GroupUserResponse(response_message='Success.',
                                response_successful = True
                                )

    ## GROUP ROLES
    @endpoints.method(GROUP_ROLES_GET_RESOURCE, GroupRoleCollection, path='groupRoleCollectionGet', http_method='POST', name='role.collection.get')
    def groupRoleCollectionGet(self, request):
        """ Get a collection of group roles """
        logging.info("groupRoleCollectionGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupRoleCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.key_id, authorized_user.key.id())

        if not group_member:
            return GroupUserResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            return GroupUserResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_group_roles:
            return GroupRoleCollection(response_message='Error: You do not have sufficient permissions to update roles for this group.', response_successful=False)

        roles = groupRolesController.get_by_groupKeyId(request.key_id)

        rolelist = []

        for role in roles:
            rolelist.append(GroupRoleResponse(
            	key_id = role.key.id(),
            	title = role.title,
            	description = role.description,
            	update_group_settings = role.update_group_settings,
            	update_group_roles = role.update_group_roles,
            	update_player_roles = role.update_player_roles,
            	create_events = role.create_events,
            	update_events = role.update_events,
                update_games = role.update_games,
            	update_servers = role.update_servers,
            	create_matches = role.create_matches,
                create_tournaments = role.create_tournaments,
                sponsor_tournaments = role.sponsor_tournaments,
                create_ads = role.create_ads,
                edit_ads = role.edit_ads,
                view_transactions = role.view_transactions,
                chat_membership = role.chat_membership,
            	applicant_role = role.applicant_role,
            	leader_role = role.leader_role,
            	order = role.order,
                groupKeyId = role.groupKeyId,
                join_group_servers = role.join_group_servers,
                join_group_server_instances = role.join_group_server_instances,
                join_group_tournaments = role.join_group_tournaments,
                drop_items_in_group_servers = role.drop_items_in_group_servers,
                pickup_items_in_group_servers = role.pickup_items_in_group_servers,
                donate_to_members = role.donate_to_members,
                metagame_faction_lead = role.metagame_faction_lead,
                metagame_team_lead = role.metagame_team_lead,
                raid_lead = role.raid_lead

            ))

        response = GroupRoleCollection(
            roles = rolelist,
            response_successful=True
        )

        return response

    @endpoints.method(GROUP_ROLES_RESOURCE, GroupRoleResponse, path='groupRoleUpdate', http_method='POST', name='role.update')
    def groupRoleUpdate(self, request):
        """ Update a group role """
        logging.info("groupRoleUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupRoleResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupRoleResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupRoleResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()

        ## get the requested group role
        if not request.key_id:
            logging.info("key_id is required")
            return GroupRoleResponse(response_message="key_id is required")

        entity = groupRolesController.get_by_key_id(int(request.key_id))

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group')
            return GroupRoleResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('role not found')
            return GroupRoleResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_group_roles:
            logging.info('You do not have sufficient permissions to update roles for this group')
            return GroupRoleResponse(response_message='Error: You do not have sufficient permissions to update roles for this group.', response_successful=False)

        ## authed and verified.

        ## TODO check to make sure there is a leader and an applicant

        if entity:
            entity.title = request.title
            entity.description = request.description
            entity.update_group_settings = request.update_group_settings
            entity.update_group_roles = request.update_group_roles
            entity.update_player_roles = request.update_player_roles
            entity.create_events = request.create_events
            entity.update_events = request.update_events
            entity.update_games = request.update_games
            entity.update_servers = request.update_servers
            entity.create_matches = request.create_matches
            entity.create_tournaments = request.create_tournaments
            entity.sponsor_tournaments = request.sponsor_tournaments
            entity.create_ads = request.create_ads
            entity.edit_ads = request.edit_ads
            entity.view_transactions = request.view_transactions
            entity.chat_membership = request.chat_membership
            entity.applicant_role = request.applicant_role
            entity.leader_role = request.leader_role
            entity.order = request.order
            entity.join_group_servers = request.join_group_servers
            entity.join_group_server_instances = request.join_group_server_instances
            entity.join_group_tournaments = request.join_group_tournaments
            entity.drop_items_in_group_servers = request.drop_items_in_group_servers
            entity.pickup_items_in_group_servers = request.pickup_items_in_group_servers
            entity.donate_to_members = request.donate_to_members
            entity.metagame_faction_lead = request.metagame_faction_lead
            entity.metagame_team_lead = request.metagame_team_lead
            entity.raid_lead = request.raid_lead

            groupRolesController.update(entity)
        else:
            ## if we don't have a role, treat it as a new role being created.
            group = groupsController.get_by_key_id(request.groupKeyId)

            new_role = groupRolesController.create(
                groupKeyId = group.key.id(),
                groupTitle = group.title,
                title = request.title,
                description = request.description,
                update_group_settings = request.update_group_settings,
                update_group_roles = request.update_group_roles,
                update_player_roles = request.update_player_roles,
                create_events = request.create_events,
                update_events = request.update_events,
                update_games = request.update_games,
                update_servers = request.update_servers,
                create_matches = request.create_matches,
                create_tournaments = request.create_tournaments,
                sponsor_tournaments = request.sponsor_tournaments,
                create_ads = request.create_ads,
                edit_ads = request.edit_ads,
                view_transactions = request.view_transactions,
                chat_membership = request.chat_membership,
                applicant_role = request.applicant_role,
                leader_role = request.leader_role,
                order = request.order,
                join_group_servers = request.join_group_servers,
                join_group_server_instances = request.join_group_server_instances,
                join_group_tournaments = request.join_group_tournaments,
                drop_items_in_group_servers = request.drop_items_in_group_servers,
                pickup_items_in_group_servers = request.pickup_items_in_group_servers,
                donate_to_members = request.donate_to_members,
                metagame_faction_lead = request.metagame_faction_lead,
                metagame_team_lead = request.metagame_team_lead,
                raid_lead = request.raid_lead
            )

        return GroupRoleResponse(response_message='success.', response_successful=True)




    @endpoints.method(GROUP_ROLES_GET_RESOURCE, GroupRoleResponse, path='groupRoleGet', http_method='POST', name='role.get')
    def groupRoleGet(self, request):
        """ Get a group role """
        logging.info("groupRoleGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupRoleResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupRoleResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupRoleResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()


        ## get the requested group role
        if not request.key_id:
            logging.info("key_id is required")
            return GroupRoleResponse(response_message="key_id is required")

        entity = groupRolesController.get_by_key_id(int(request.key_id))

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(int(request.groupKeyId), authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group.')
            return GroupRoleResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('User Role not found.')
            return GroupRoleResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_group_roles:
            logging.info('You do not have sufficient permissions to update roles for this group.')
            return GroupRoleResponse(response_message='Error: You do not have sufficient permissions to update roles for this group.', response_successful=False)

        ## authed and verified.

        if entity:
            logging.info('role found')
            response = GroupRoleResponse(
                title = entity.title,
                description = entity.description,

                update_group_settings = entity.update_group_settings,
                update_group_roles = entity.update_group_roles,
                update_player_roles = entity.update_player_roles,
                create_events = entity.create_events,
                update_events = entity.update_events,
                update_games = entity.update_games,
                update_servers = entity.update_servers,
                create_matches = entity.create_matches,
                create_tournaments = entity.create_tournaments,
                sponsor_tournaments = entity.sponsor_tournaments,
                create_ads = entity.create_ads,
                edit_ads = entity.edit_ads,
                view_transactions = entity.view_transactions,
                chat_membership = entity.chat_membership,
                applicant_role = entity.applicant_role,
                leader_role = entity.leader_role,
                order = entity.order,
                join_group_servers = entity.join_group_servers,
                join_group_server_instances = entity.join_group_server_instances,
                join_group_tournaments = entity.join_group_tournaments,
                drop_items_in_group_servers = entity.drop_items_in_group_servers,
                pickup_items_in_group_servers = entity.pickup_items_in_group_servers,
                donate_to_members = entity.donate_to_members,
                metagame_faction_lead = entity.metagame_faction_lead,
                metagame_team_lead = entity.metagame_team_lead,
                raid_lead = entity.raid_lead
            )

            return response
        else:
            logging.info('role not found')
            return GroupRoleResponse(response_message='Error: The Role was not found.', response_successful=False)

    # GROUP GAMES

    @endpoints.method(GROUP_GAME_CONNECT_RESOURCE, GroupGameResponse, path='groupGameCreate', http_method='POST', name='game.create')
    def groupGameCreate(self, request):
        """ Create a connection between a game and a group """
        logging.info("groupGameCreate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupGameResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupGameResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupGameResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        groupGamesController = GroupGamesController()
        gameController = GamesController()

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(request.groupKeyId, authorized_user.key.id())

        if not group_member:
            return GroupGameResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the group
        group = groupsController.get_by_key_id(group_member.groupKeyId)
        if not group:
            return GroupGameResponse(response_message='Error: Group not found.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            return GroupGameResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_games:
            return GroupGameResponse(response_message='Error: You do not have sufficient permissions to update games for this group.', response_successful=False)

        ## get the game
        game = gameController.get_by_key_id(request.gameKeyId)

        if not game:
            return GroupGameResponse(response_message='Error: Game not found with the specified key.', response_successful=False)

        ## check to see if it is already connected
        existing_connection = groupGamesController.get_by_groupKeyId_gameKeyId(group.key.id(), game.key.id())
        if existing_connection:
            return GroupGameResponse(response_message='Error: Game already connected.', response_successful=False)

        ## authed and verified.

        ## create the game connection
        group_game = groupGamesController.create(
            groupKeyId = group.key.id(),
            groupTitle = group.title,
        	gameKeyId = game.key.id(),
            gameTitle = game.title,
            show_game_on_group_page = request.show_game_on_group_page
        )

        ## update firebase - checks for visibility inside the task
        taskUrl='/task/group/game/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': group_game.key.id(), 'groupKeyId': group_game.groupKeyId, 'gameKeyId': group_game.gameKeyId}, countdown = 2,)

        return GroupGameResponse(response_message='Success.  Group Game Created.', response_successful=True)

    @endpoints.method(GROUP_GAME_CONNECT_RESOURCE, GroupGameResponse, path='groupGameGet', http_method='POST', name='game.get')
    def groupGameGet(self, request):
        """ Get a group game """
        logging.info("groupGameGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupGameResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupGameResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupGameResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        groupGamesController = GroupGamesController()

        ## get the requested group role
        if not request.key_id:
            logging.info("key_id is required")
            return GroupGameResponse(response_message="key_id is required")

        entity = groupGamesController.get_by_key_id(int(request.key_id))

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(int(entity.groupKeyId), authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group.')
            return GroupGameResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('User Role not found.')
            return GroupGameResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_games:
            return GroupGameResponse(response_message='Error: You do not have sufficient permissions to update games for this group.', response_successful=False)

        ## authed and verified.

        if entity:
            logging.info('game found')
            response = GroupGameResponse(
                discordWebhook = entity.discordWebhook,
                gameKeyId = entity.gameKeyId,
                discord_subscribe_game_event_feeds = entity.discord_subscribe_game_event_feeds,
                discord_subscribe_game_event_feed_kills = entity.discord_subscribe_game_event_feed_kills,
                discord_subscribe_game_event_feed_wins = entity.discord_subscribe_game_event_feed_wins,
                discord_subscribe_game_ad_status_changes = entity.discord_subscribe_game_ad_status_changes,
                show_game_on_group_page = entity.show_game_on_group_page,
                inGameTextureServingUrl = entity.inGameTextureServingUrl,
                response_successful = True,
                response_message = "Success."
            )

            return response
        else:
            logging.info('game not found')
            return GroupGameResponse(response_message='Error: The Game was not found.', response_successful=False)

    @endpoints.method(GROUP_GAME_EDIT_RESOURCE, GroupGameResponse, path='groupGameUpdate', http_method='POST', name='game.update')
    def groupGameUpdate(self, request):
        """ Update a group game """
        logging.info("groupGameUpdate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupGameResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupGameResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GroupGameResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        groupGamesController = GroupGamesController()


        ## get the requested group game
        if not request.key_id:
            logging.info("key_id is required")
            return GroupGameResponse(response_message="key_id is required")

        entity = groupGamesController.get_by_key_id(int(request.key_id))

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(int(entity.groupKeyId), authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group.')
            return GroupGameResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('User Role not found.')
            return GroupGameResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_games:
            return GroupGameResponse(response_message='Error: You do not have sufficient permissions to update games for this group.', response_successful=False)

        ## authed and verified.

        entity.discordWebhook = request.discordWebhook
        entity.discord_subscribe_game_event_feeds = request.discord_subscribe_game_event_feeds
        entity.discord_subscribe_game_event_feed_kills = request.discord_subscribe_game_event_feed_kills
        entity.discord_subscribe_game_event_feed_wins = request.discord_subscribe_game_event_feed_wins
        entity.discord_subscribe_game_ad_status_changes = request.discord_subscribe_game_ad_status_changes

        entity.show_game_on_group_page = request.show_game_on_group_page
        entity.inGameTextureServingUrl = request.inGameTextureServingUrl

        groupGamesController.update(entity)

        response = GroupGameResponse(
            discordWebhook = entity.discordWebhook,
            discord_subscribe_game_event_feeds = entity.discord_subscribe_game_event_feeds,
            discord_subscribe_game_event_feed_kills = entity.discord_subscribe_game_event_feed_kills,
            discord_subscribe_game_event_feed_wins = entity.discord_subscribe_game_event_feed_wins,
            discord_subscribe_game_ad_status_changes = entity.discord_subscribe_game_ad_status_changes,
            response_successful = True,
            response_message = "Success."
        )

        return response

    @endpoints.method(GROUP_GAME_CONNECT_RESOURCE, GroupGameResponse, path='groupGameDelete', http_method='POST', name='game.delete')
    def groupGameDelete(self, request):
        """ Delete a group game - PROTECTED """
        logging.info("groupGameDelete")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GroupGameResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GroupGameResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        ## ONLY allow this from authorized domains
        request_origin = self.request_state.headers['origin']
        logging.info("request_origin: %s" %request_origin)
        if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
            logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
            return GroupGameResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        if not authorized_user:
            logging.info('no user record found')
            return GroupGameResponse(response_message='Error: No User Record Found. ', response_successful=False)

        groupsController = GroupsController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        groupGamesController = GroupGamesController()

        ## get the requested group game
        if not request.key_id:
            logging.info("key_id is required")
            return GroupGameResponse(response_message="key_id is required")

        entity = groupGamesController.get_by_key_id(int(request.key_id))

        ## check if the player is already a member
        group_member = groupUsersController.get_by_groupKeyId_userKeyId(int(entity.groupKeyId), authorized_user.key.id())

        if not group_member:
            logging.info('Not a member of this group.')
            return GroupGameResponse(response_message='Error: Not a member of this group.', response_successful=False)

        # get the role
        group_member_role = groupRolesController.get_by_key_id(group_member.roleKeyId)
        if not group_member_role:
            logging.info('User Role not found.')
            return GroupGameResponse(response_message='Error: Role not found.', response_successful=False)

        if not group_member_role.update_games:
            return GroupGameResponse(response_message='Error: You do not have sufficient permissions to update games for this group.', response_successful=False)

        ## authed and verified.

        ## update firebase - this will delete it
        taskUrl='/task/group/game/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': entity.key.id(), 'groupKeyId': entity.groupKeyId, 'gameKeyId': entity.gameKeyId}, countdown = 2,)

        groupGamesController.delete(entity)

        response = GroupGameResponse(
            response_successful = True,
            response_message = "Success."
        )

        return response
