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

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.models.groups import *
from apps.uetopia.models.group_users import *
from apps.uetopia.models.group_roles import *
from apps.uetopia.models.group_games import *

from apps.uetopia.models.teams import *

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController

from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

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


@endpoints.api(name="teams", version="v1", description="Teams API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class TeamsApi(remote.Service):
    @endpoints.method(TEAM_CREATE_RESOURCE, TeamResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        """ Create a team """
        logging.info("create")
        logging.info(request)
        logging.info(request.gameKeyId)
        logging.info(request.gameKeyIdStr)


        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamResponse(response_message='Error: No User Record Found. ', response_successful=False)


        userController = UsersController()
        gameController = GamesController()
        gameModeController = GameModesController()
        gamePlayerController = GamePlayersController()
        groupController = GroupsController()

        tournamentController = TournamentsController()
        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()


        ## get the game
        if request.gameKeyId:
            gameKeyId = request.gameKeyId
        else:
            logging.info('no gameKeyId found')
            ## trying the string version - UE client sends this way.
            if request.gameKeyIdStr:
                gameKeyId = int(request.gameKeyIdStr)
            else:
                logging.info('no gameKeyIdStr found')
                return TeamResponse(response_message='Error: No gameKeyId Found. ', response_successful=False)

        game = gameController.get_by_key_id(gameKeyId)
        if not game:
            logging.info('no game record found')
            return TeamResponse(response_message='Error: No game Record Found. ', response_successful=False)


        ## Check to see if this user is a member of a different team.
        existing_team_membership = teamMembersController.get_by_gameKeyId_userKeyId(game.key.id(), target_user.key.id())
        if existing_team_membership:
            logging.info('Existing team found - Aborting')
            return TeamResponse(response_message='Error: You are already a member of a team.  Leave your current one first.', response_successful=False)

        ## Make sure there is a game player for this user
        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(gameKeyId, authorized_user.key.id())
        if not game_player:
            logging.info('No Game Player found - Aborting')
            return TeamResponse(response_message='Error: You are not authorized for play in this game.  Hit play on the website first.', response_successful=False)

        ## any other checks needed here?

        title = request.title
        if not title:
            title = authorized_user.title + "'s Team"

        if request.teamSize > 1:
            teamFull = False
            recruiting = True
        else:
            teamFull = True
            recruiting = False
        if request.teamSize > TEAM_MAXIMUM_SIZE:
            request.teamSize = TEAM_MAXIMUM_SIZE

        team = teamController.create(
            title = title,
            description = request.description,
            pug = True,
            #teamAvatarTheme = player.avatar_theme,

            gameKeyId = game.key.id(),
            gameTitle = game.title,

            #groupMembersOnly = False, ## TODO implement this?
            #groupKey = request
            #groupTitle = ndb.StringProperty()

            captainPlayerKeyId = authorized_user.key.id(),
            captainPlayerTitle = authorized_user.title,

            teamSizeMax = game.partySizeMaximum,
            teamSizeCurrent = 1,
            teamFull = teamFull,

            ## State flags
            initialized = False,
            recruiting = recruiting,
            inTournament = False,
            activeInTournament = False,
            inMatch = False,
            purged = False,
        )

        ## Add the captain team player record

        team_player = teamMembersController.create(
            teamKeyId = team.key.id(),
            teamTitle = team.title,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            userFirebaseUser = authorized_user.firebaseUser,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            gamePlayerKeyId = game_player.key.id(),
            #playerAvatarTheme = player.avatar_theme,
            invited = False,
            joined = True, ## TODO double check that the user should join upon create
            applicant = False,
            approved = True,
            captain = True,
            denied = False,

            order = 1,
        )

        ## Create the team chat channel, and subscribe the captain to it.
        party_chat_title = "party chat"
        party_chat_channel = chatChannelController.create(
            title = party_chat_title,
            channel_type = 'team',
            #adminUserKeyId = authorized_user.key.id(),
            refKeyId = team.key.id(),
            gameKeyId = game.key.id(),
            max_subscribers = 20
        )

        subscriber = chatChannelSubscribersController.create(
            online = True,
            chatChannelKeyId = party_chat_channel.key.id(),
            chatChannelTitle = party_chat_channel.title,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            userFirebaseUser = authorized_user.firebaseUser,
            post_count = 0,
            chatChannelRefKeyId = team.key.id(),
            channel_type = 'team',
            #chatChannelOwnerKeyId = authorized_user.key.id()
        )

        chat_message = "> Joined party chat"

        ## push the chat channel list and a chat message

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


        ## TODO Sense


        return TeamResponse(key_id = team.key.id(),
                title = team.title,
                description = team.description,
                teamSizeMax =team.teamSizeMax,
                teamSizeCurrent = team.teamSizeCurrent,
                teamFull = team.teamFull,
                initialized = team.initialized,
                recruiting = team.recruiting,
                inTournament = team.inTournament,
                inMatch = team.inMatch,
                message='Success. Team Created.')

    @endpoints.method(TEAM_COLLECTION_PAGE_RESOURCE, TeamCollection, path='teamCollectionGet', http_method='POST', name='collection.get')
    def teamCollectionGet(self, request):
        """ Get a collection of teams """
        logging.info("teamCollectionGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamCollection(response_message='Error: No User Record Found. ', response_successful=False)

        ## get the game
        if request.gameKeyId:
            gameKeyId = request.gameKeyId
        else:
            logging.info('no gameKeyId found')
            ## trying the string version - UE client sends this way.
            if request.gameKeyIdStr:
                gameKeyId = int(request.gameKeyIdStr)
            else:
                logging.info('no gameKeyIdStr found')
                return TeamCollection(response_message='Error: No gameKeyId Found. ', response_successful=False)

        #game = gameController.get_by_key_id(gameKeyId)
        #if not game:
        #    logging.info('no game record found')
        #    return TeamResponse(response_message='Error: No game Record Found. ', response_successful=False)

        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        entities = teamMembersController.list_by_gameKeyId_userKeyId(gameKeyId, authorized_user.key.id())


        ## If there is a team membership, push it out to everyone.
        ## TODO, move this out to a proper "logged in and joined" API call

        existing_team_membership = teamMembersController.get_by_gameKeyId_userKeyId(gameKeyId, authorized_user.key.id())
        if existing_team_membership:
            logging.info('found an existing team member for this user')

            ## queue up the task to send a message to all team members
            taskUrl='/task/team/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': existing_team_membership.teamKeyId}, countdown = 2,)

        else:
            logging.info('no team member found')

            ## push out a team empty message
            ## Send a push to the leaving member.  WE're deleting them so they won't get it otherwise.
            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            team = {'purged': True, 'members': [], 'userIsCaptain': True}

            team_json = json.dumps(team)

            #try:
            URL = "%s/user/%s/team/0" % (HEROKU_SOCKETIO_SERVER, authorized_user.firebaseUser)
            resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  team_json,
                                  headers=headers)

            logging.info(resp)
            logging.info(content)
            #except:
            #    logging.error('Heroku Error')



        entity_list = []

        for entity in entities:
            entity_list.append(TeamResponse(
                key_id = entity.key.id(),
                title = entity.teamTitle
            ))

        response = TeamCollection(
            teams = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(TEAM_GET_RESOURCE, TeamResponse, path='userInvite', http_method='POST', name='user.invite')
    def userInvite(self, request):
        """ Invite a user to a team """
        logging.info("userInvite")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gameController = GamesController()

        ## get the game
        if request.gameKeyId:
            gameKeyId = request.gameKeyId
        else:
            logging.info('no gameKeyId found - trying gameKeyIdStr')
            ## trying the string version - UE client sends this way.
            if request.gameKeyIdStr:
                gameKeyId = int(request.gameKeyIdStr)
            else:
                logging.info('no gameKeyIdStr found')
                return TeamResponse(response_message='Error: No gameKeyId Found. ', response_successful=False)

        game = gameController.get_by_key_id(gameKeyId)
        if not game:
            logging.info('no game found')
            return TeamResponse(response_message='Error: No game Found. ', response_successful=False)

        teamController = TeamsController()
        teamMembersController = TeamMembersController()
        gamePlayerController = GamePlayersController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()


        authorized_user_game_player = gamePlayerController.get_by_gameKeyId_userKeyId(gameKeyId, authorized_user.key.id())
        if not authorized_user_game_player:
            logging.info('No Game Player found - Aborting')
            return TeamResponse(response_message='Error: You are not authorized for play in this game.  Hit play on the website first.', response_successful=False)

        ## get the team
        ## TODO if no key is supplied, just look up to see if we have one for this authenticated_user in the database?

        ## Changing this around
        ## Only one team/party per player per game
        ## Ignore the teamKeyID coming from the client.

        #if request.teamKeyIdStr:
        #    logging.info('teamKeyIdStr found')
        #    logging.info(request.teamKeyIdStr)
        #    teamKeyId = int(request.teamKeyIdStr)
        #    team = teamController.get_by_key_id(teamKeyId)
        #    if not team:
        #        logging.info('no team found')
        #        return TeamResponse(response_message='Error: No team Found. ', response_successful=False)
        #else:
        #    logging.info('no teamKeyIdStr found')

        ## Check to see if there is a team member for the requesting user
        team = None
        party_chat_channel = None
        existing_team_member = teamMembersController.get_by_gameKeyId_userKeyId(gameKeyId, authorized_user.key.id())
        if existing_team_member:
            logging.info('existing_team_member found')
            if existing_team_member.captain:
                logging.info('existing_team_member is captain')
                team = teamController.get_by_key_id(existing_team_member.teamKeyId)
                party_chat_channel = chatChannelController.get_by_channel_type_refKeyId("team", team.key.id())
            else:
                logging.info('existing_team_member is NOT captain')
                return TeamResponse(response_message='Error: existing_team_member is NOT captain. ', response_successful=False)
        else:
            logging.info('existing team member not found')


        ## If no team was found, create one
        if not team:
            title = authorized_user.title + "'s Team"

            team = teamController.create(
                title = title,
                description = "created via party invite",
                pug = True,
                #teamAvatarTheme = player.avatar_theme,

                gameKeyId = game.key.id(),
                gameTitle = game.title,

                #groupMembersOnly = False, ## TODO implement this?
                #groupKey = request
                #groupTitle = ndb.StringProperty()

                captainPlayerKeyId = authorized_user.key.id(),
                captainPlayerTitle = authorized_user.title,

                teamSizeMax = game.partySizeMaximum,
                teamSizeCurrent = 1,
                teamFull = False,

                ## State flags
                initialized = False,
                recruiting = True,
                inTournament = False,
                activeInTournament = False,
                inMatch = False,
                purged = False,
            )

            ## Add the captain team player record

            team_player = teamMembersController.create(
                teamKeyId = team.key.id(),
                teamTitle = team.title,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                userFirebaseUser = authorized_user.firebaseUser,
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                gamePlayerKeyId = authorized_user_game_player.key.id(),
                #playerAvatarTheme = player.avatar_theme,
                invited = False,
                joined = True, ## TODO double check that the user should join upon create
                applicant = False,
                approved = True,
                captain = True,
                denied = False,

                order = 1,
            )

            ## Create the team chat channel, and subscribe the captain to it.
            party_chat_title = "party chat"
            party_chat_channel = chatChannelController.create(
                title = party_chat_title,
                channel_type = 'team',
                #adminUserKeyId = authorized_user.key.id(),
                refKeyId = team.key.id(),
                gameKeyId = game.key.id(),
                max_subscribers = 20
            )

            subscriber = chatChannelSubscribersController.create(
                online = True,
                chatChannelKeyId = party_chat_channel.key.id(),
                chatChannelTitle = party_chat_channel.title,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                userFirebaseUser = authorized_user.firebaseUser,
                post_count = 0,
                chatChannelRefKeyId = team.key.id(),
                channel_type = 'team',
                #chatChannelOwnerKeyId = authorized_user.key.id()
            )

            chat_message = "> Joined party chat"

            ## push the chat channel list and a chat message

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




        ## get the target user
        if request.userKeyIdStr:
            logging.info('userKeyIdStr: %s' % request.userKeyIdStr)
        else:
            logging.info('no userKeyIdStr found')
            return TeamResponse(response_message='Error: No userKeyIdStr Found. ', response_successful=False)

        userKeyId = int(request.userKeyIdStr)
        target_user = UsersController().get_by_key_id(userKeyId)
        if not target_user:
            logging.info('no target_user found')
            return TeamResponse(response_message='Error: No target_user Found. ', response_successful=False)

        ## get target game_player
        target_user_game_player = gamePlayerController.get_by_gameKeyId_userKeyId(gameKeyId, target_user.key.id())
        if not target_user_game_player:
            logging.info('No Target Game Player found - Aborting')
            return TeamResponse(response_message='Error: That user is not authorized for play in this game.  Have them hit play on the website first.', response_successful=False)


        ## set up the http request
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        team.userKeyId = target_user.key.id()
        team.senderKeyId = authorized_user.key.id()
        team.senderUserTitle = authorized_user.title

        team_json = json.dumps(team.to_json_with_UserIds())

        ## Check to see if this target_user is a member of a different team.
        existing_team_membership = teamMembersController.get_by_gameKeyId_userKeyId(team.gameKeyId, target_user.key.id())
        ## check to see if it's the same or different team
        if existing_team_membership:
            logging.info('found an existing team member for this user')
            if existing_team_membership.teamKeyId == team.key.id():
                logging.info('Existing team member is part of this team. - Resending invite.')
                if not existing_team_membership.invited:
                    logging.info('resetting invited bool')
                    existing_team_membership.invited = True
                    existing_team_membership.invitedByUserKeyId = authorized_user.key.id()
                    teamMembersController.update(existing_team_membership)

            else:
                logging.info('Existing team member is part of a different team.')

                chat_message = "Error: %s is a member of a different team. " % target_user.title

                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                                    "message": chat_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })


                return TeamResponse(response_message='Error: Player is a member of a different team. ', response_successful=False)
        else:
            logging.info('Team Member does not exist - Creating one')
            ## create a groupMember - set it to invited
            ## don't do this here?  Wait for a user to accept the invitation ?
            team_member = teamMembersController.create(
                teamKeyId = team.key.id(),
                teamTitle = team.title,
                userKeyId = target_user.key.id(),
                userTitle = target_user.title,
                userFirebaseUser = target_user.firebaseUser,
                invitedByUserKeyId = authorized_user.key.id(),
                gameKeyId = team.gameKeyId,
                gameTitle = team.gameTitle,
                gamePlayerKeyId = target_user_game_player.key.id(),
                #playerAvatarTheme = player.avatar_theme,
                invited = True,
                joined = False,
                applicant = False,
                approved = True,
                captain = False,
                denied = False,

                order = 100,
            )

        ## queue up the task to send a message to all team members
        taskUrl='/task/team/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)

        ## push a message out to the socketserver
        URL = "%s/user/%s/party/invite/send" % (HEROKU_SOCKETIO_SERVER, target_user.firebaseUser)
        resp, content = http_auth.request(URL,
                            ##"PATCH",
                          "PUT", ## Write or replace data to a defined path,
                          team_json,
                          headers=headers)

        return TeamResponse(response_message='Success.  User Invited. ', response_successful=True)

    @endpoints.method(TEAM_GET_RESOURCE, TeamResponse, path='userInviteReject', http_method='POST', name='user.invite.reject')
    def userInviteReject(self, request):
        """ Reject a team invitation """
        logging.info("userInviteReject")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamResponse(response_message='Error: No User Record Found. ', response_successful=False)

        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        invitedByUserKeyId = int(request.userKeyIdStr)
        invited_by_user = UsersController().get_by_key_id(invitedByUserKeyId)
        if not invited_by_user:
            logging.info('no invited_by_user found')
            return TeamResponse(response_message='Error: No invited_by_user Found. ', response_successful=False)

        pending_invite_team_member = teamMembersController.get_invited_by_invitedByUserKeyId_userKeyId(invitedByUserKeyId, authorized_user.key.id())
        if not pending_invite_team_member:
            logging.info('no pending_invite_team_member found')
            return TeamResponse(response_message='Error: No pending_invite_team_member Found. ', response_successful=False)

        team = teamController.get_by_key_id(pending_invite_team_member.teamKeyId)
        if not team:
            logging.info('no team found')
            return TeamResponse(response_message='Error: No team Found. ', response_successful=False)

        ## Any other checks?

        ## delete the pending team member
        teamMembersController.delete(pending_invite_team_member)

        ## push
        ## set up the http request
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        ## queue up the task to send a message to all team members
        taskUrl='/task/team/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)

        ## push a message out to the socketserver

        response_json = json.dumps({'response': 'Rejected',
                                    'key_id': str(team.key.id()),
                                    'senderKeyId': str(authorized_user.key.id())
                                    })

        ## this is to 	TriggerOnPartyInviteResponseReceivedDelegates
        URL = "%s/user/%s/party/invite/response" % (HEROKU_SOCKETIO_SERVER, invited_by_user.firebaseUser)
        resp, content = http_auth.request(URL,
                            ##"PATCH",
                          "PUT", ## Write or replace data to a defined path,
                          response_json,
                          headers=headers)

        return TeamResponse(response_message='Success.  Invitation Rejected. ', response_successful=True)


    @endpoints.method(TEAM_GET_RESOURCE, TeamResponse, path='userInviteAccept', http_method='POST', name='user.invite.accept')
    def userInviteAccept(self, request):
        """ Accept a team invitation """
        logging.info("userInviteAccept")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamResponse(response_message='Error: No User Record Found. ', response_successful=False)

        teamController = TeamsController()
        teamMembersController = TeamMembersController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        invitedByUserKeyId = int(request.userKeyIdStr)
        invited_by_user = UsersController().get_by_key_id(invitedByUserKeyId)
        if not invited_by_user:
            logging.info('no invited_by_user found')
            return TeamResponse(response_message='Error: No invited_by_user Found. ', response_successful=False)

        pending_invite_team_member = teamMembersController.get_invited_by_invitedByUserKeyId_userKeyId(invitedByUserKeyId, authorized_user.key.id())
        if not pending_invite_team_member:
            logging.info('no pending_invite_team_member found')
            return TeamResponse(response_message='Error: No pending_invite_team_member Found. ', response_successful=False)

        team = teamController.get_by_key_id(pending_invite_team_member.teamKeyId)
        if not team:
            logging.info('no team found')
            return TeamResponse(response_message='Error: No team Found. ', response_successful=False)

        ## Any other checks?

        ## set flags on team member
        pending_invite_team_member.joined = True
        pending_invite_team_member.invited = False
        teamMembersController.update(pending_invite_team_member)

        ## subscribe the user to the party chat channel
        party_chat_channel = chatChannelController.get_by_channel_type_refKeyId("team", team.key.id())
        if party_chat_channel:
            subscriber = chatChannelSubscribersController.create(
                online = True,
                chatChannelKeyId = party_chat_channel.key.id(),
                chatChannelTitle = party_chat_channel.title,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                userFirebaseUser = authorized_user.firebaseUser,
                post_count = 0,
                chatChannelRefKeyId = team.key.id(),
                channel_type = 'team',
                #chatChannelOwnerKeyId = authorized_user.key.id()
            )

            chat_message = "> Joined party chat"

            ## push the chat channel list and a chat message

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


        ## push
        ## set up the http request
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        ## queue up the task to send a message to all team members
        taskUrl='/task/team/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)

        ## push a message out to the socketserver

        response_json = json.dumps({'response': 'Accepted',
                                    'key_id': str(team.key.id()),
                                    'senderKeyId': str(authorized_user.key.id())
                                    })

        ## this is to 	TriggerOnPartyInviteResponseReceivedDelegates
        URL = "%s/user/%s/party/invite/response" % (HEROKU_SOCKETIO_SERVER, invited_by_user.firebaseUser)
        resp, content = http_auth.request(URL,
                            ##"PATCH",
                          "PUT", ## Write or replace data to a defined path,
                          response_json,
                          headers=headers)

        ## TODO deal with tournament stuff

        return TeamResponse(response_message='Success.  Invitation Accepted. ', response_successful=True)


    @endpoints.method(TEAM_GET_RESOURCE, TeamResponse, path='join', http_method='POST', name='join')
    def join(self, request):
        """ Join a team """
        logging.info("join")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## get the game
        if request.gameKeyId:
            gameKeyId = request.gameKeyId
        else:
            logging.info('no gameKeyId found')
            ## trying the string version - UE client sends this way.
            if request.gameKeyIdStr:
                gameKeyId = int(request.gameKeyIdStr)
            else:
                logging.info('no gameKeyIdStr found')
                return TeamResponse(response_message='Error: No gameKeyId Found. ', response_successful=False)


        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        ## get the team
        ## TODO if no key is supplied, just look up to see if we have one for this authenticated_user in the database?
        if not request.teamKeyIdStr:
            logging.info('no teamKeyIdStr found')
            return TeamResponse(response_message='Error: No teamKeyIdStr Found. ', response_successful=False)

        teamKeyId = int(request.teamKeyIdStr)
        team = teamController.get_by_key_id(teamKeyId)
        if not team:
            logging.info('no team found')
            return TeamResponse(response_message='Error: No team Found. ', response_successful=False)

        ## check to see if this user already has a team membership record
        team_member = teamMembersController.get_by_teamKeyId_userKeyId(team.key.id(), target_user.key.id())
        if team_member:
            logging.info('team member found')
            if team_member.invited:
                logging.info('team member is invited')
                if team_member.approved:
                    logging.info('team member is approved')
                    ## TODO other checks?
                    if not team_member.joined:
                        logging.info('not joined - setting it')
                        team_member.joined = True

                        teamMembersController.update(team_member)

                    # send the push out to the socket server
                    # doing this in a task, because we need to send a push out to every member of the party.

                    taskUrl='/task/team/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)



                    ## TODO any other housekeeping?

                    return TeamResponse(response_message='Success.  Team Joined ', response_successful=True)

        return TeamResponse(response_message='Error.', response_successful=False)

    @endpoints.method(TEAM_GET_RESOURCE, TeamResponse, path='leave', http_method='POST', name='leave')
    def leave(self, request):
        """ Leave a team """
        logging.info("leave")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TeamResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return TeamResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TeamResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## get the game
        if request.gameKeyId:
            gameKeyId = request.gameKeyId
        else:
            logging.info('no gameKeyId found')
            ## trying the string version - UE client sends this way.
            if request.gameKeyIdStr:
                gameKeyId = int(request.gameKeyIdStr)
            else:
                logging.info('no gameKeyIdStr found')
                return TeamResponse(response_message='Error: No gameKeyId Found. ', response_successful=False)


        teamController = TeamsController()
        teamMembersController = TeamMembersController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        ## get the team_member
        team_member = teamMembersController.get_by_gameKeyId_userKeyId(gameKeyId, authorized_user.key.id())
        if not team_member:
            logging.info('no team_memberfound')
            return TeamResponse(response_message='Error: No team_member Found. ', response_successful=False)

        ## get the team
        team = teamController.get_by_key_id(team_member.teamKeyId)
        if not team:
            logging.info('no team found')
            return TeamResponse(response_message='Error: No team Found. ', response_successful=False)

        ## prevent leaving if the team is in tournament queue
        if team.inTournament:
            logging.info('leaving the team while in tournament queue is not allowed')
            return TeamResponse(response_message="Error: You can't leave the team while the team is in a tournament.  ", response_successful=False)

        ## If there are still team_members
        ## Check for leadership
        ## If the user leaving is the leader promote someone else.

        delete_team = True

        all_team_members = teamMembersController.get_by_teamKeyId(team.key.id())
        if len(all_team_members) > 2:
            logging.info('There are still members of this team')
            if team_member.captain:
                logging.info('The player that is leaving is the captain.')
                for a_team_member in all_team_members:
                    if team_member.key.id() != a_team_member.key.id() and a_team_member.joined:
                        logging.info('promoting someone else')
                        a_team_member.captain = True
                        teamMembersController.update(a_team_member)
                        delete_team = False
                        break
        else:
            logging.info('Not enough players in team - dumping')

        ## Send a push to the leaving member.  WE're deleting them so they won't get it otherwise.
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        team.purged = True ## Indicate to UE game clients that we are deleting!
        team.members = []
        team.userIsCaptain = None
        team_json = json.dumps(team.to_json_with_members())

        try:
            URL = "%s/user/%s/team/%s" % (HEROKU_SOCKETIO_SERVER, team_member.userFirebaseUser, team_member.teamKeyId)
            resp, content = http_auth.request(URL,
                                ##"PATCH",
                              "PUT", ## Write or replace data to a defined path,
                              team_json,
                              headers=headers)

            logging.info(resp)
            logging.info(content)
        except:
            logging.error('Heroku Error')

        ## delete the chat channel subscriber for the leaving member
        party_chat_channel = chatChannelController.get_by_channel_type_refKeyId("team", team.key.id())
        if party_chat_channel:
            subscriber = chatChannelSubscribersController.get_by_channel_and_user(party_chat_channel.key.id(), authorized_user.key.id())
            if subscriber:
                chatChannelSubscribersController.delete(subscriber)

                chat_message = "> Left party chat"

                ## push the chat channel list and a chat message

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

        ## remove the leaving team member
        teamMembersController.delete(team_member)

        if delete_team:
            taskUrl='/task/team/delete'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 0,)

        else:
            taskUrl='/task/team/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)


        return TeamResponse(response_message='Success.  Team Left ', response_successful=True)
