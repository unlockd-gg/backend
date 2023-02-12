import endpoints
import logging
import uuid
import urllib
import json
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
from protorpc import remote
from google.appengine.api import taskqueue

from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection


##from apps.uetopia.providers import firebase_helper


from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.user_relationships import UserRelationshipsController
from apps.uetopia.controllers.match_players import MatchPlayersController

from apps.uetopia.models.users import Users, UserResponse, USER_RESOURCE, UserCollection, USER_COLLECTION_PAGE_RESOURCE
from apps.uetopia.models.user_relationships import *

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="user_relationships", version="v1", description="User Relationships API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class UserRelationshipsApi(remote.Service):
    @endpoints.method(USER_RELATIONSHIP_CREATE_RESOURCE, UserRelationshipGetResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        """ Create a relationship between two users """
        logging.info("userRelationshipCreate")
        urController = UserRelationshipsController()
        uController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserRelationshipGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserRelationshipGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))

        ## get initiating user
        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            return UserRelationshipGetResponse(response_message='Error: User Record Missing.', response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))

        ## self target
        if authorized_user.key.id() == request.key_id:
            return UserRelationshipGetResponse(response_message='Error: You cannot add yourself to the friends list.', response_successful=False,
                                                    userTargetKeyId = request.key_id,
                                                    userTargetKeyIdStr = str(request.key_id))

        ## get target
        target_user = uController.get_by_key_id(request.key_id)
        if not target_user:
            return UserRelationshipGetResponse(response_message='Error: Could not get target from key.',  response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))

        ## check if relationship already exists
        existing_relationship = urController.get_by_userKeyId_userTargetKeyId(authorized_user.key.id(), target_user.key.id())

        update = False

        if existing_relationship:
            if existing_relationship.friend:
                logging.info('Relationship already exists.')

                ## resend the push invite
                # Push an invite out to the target user via socket server
                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                headers = {"Content-Type": "application/json"}

                push_payload = {'senderKeyId': str(authorized_user.key.id()), 'senderUserTitle': authorized_user.title}

                payload_json = json.dumps(push_payload)

                #try:
                URL = "%s/user/%s/friend/invite/send" % (HEROKU_SOCKETIO_SERVER, target_user.firebaseUser)
                resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      payload_json,
                                      headers=headers)

                logging.info(resp)
                logging.info(content)

                return UserRelationshipGetResponse(response_message='Error: Relationship already exists.', response_successful=False,
                                                    userTargetKeyId = request.key_id,
                                                    userTargetKeyIdStr = str(request.key_id))
            else:
                update = True

        ## check if there is a corresponding friend
        corresponding_relationship = urController.get_by_userKeyId_userTargetKeyId( target_user.key.id(), authorized_user.key.id())

        friendConfirmed = False

        if corresponding_relationship:
            if corresponding_relationship.friend:
                friendConfirmed = True
                corresponding_relationship.friendConfirmed = True
                urController.update(corresponding_relationship)

                ## TODO achievements


        if update:
            existing_relationship.friend = request.friend
            existing_relationship.friendConfirmed = friendConfirmed
            existing_relationship.ignore = request.ignore
            existing_relationship.nickname = request.nickname
            urController.update(existing_relationship)
            relationship = existing_relationship
        else:
            ## add the relationship
            relationship = urController.create(
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                userFirebaseUser = authorized_user.firebaseUser,
                userTargetKeyId = target_user.key.id(),
                userTargetTitle = target_user.title,
                userTargetFirebaseUser = target_user.firebaseUser,
                userTargetPicture = target_user.picture,
                friend = request.friend,
                friendConfirmed = friendConfirmed,
                ignore = request.ignore,
                nickname = request.nickname,
                online = target_user.online
            )

        ## Sense
        """
        SenseController().create(
            target_type = 'User',
            target_key = user.key.id(),
            target_title = user.title,
            ref_type = 'User',
            ref_key = target_user.key.id(),
            action = 'Friend Added',
            title = '%s Added a Friend %s' % (user.title, target_user.title),
            description = '%s Added a Friend %s' % (user.title, target_user.title),
            ##amount = request.amount
        )
        """
        if friendConfirmed:
            description = "%s is now your friend" %(authorized_user.title)
        else:
            description = "%s wants to be friends" %(authorized_user.title)

        # send an alert to the target user
        ## push an alert out to firebase
        taskUrl='/task/user/alert/create'
        action_button_sref = '#/user/' + str(authorized_user.key.id())
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': target_user.firebaseUser,
                                                                        'material_icon': MATERIAL_ICON_FRIENDS,
                                                                        'importance': 'md-primary',
                                                                        ## TODO this message can be more helpful
                                                                        'message_text': description,
                                                                        'action_button_color': 'primary',
                                                                        'action_button_sref': action_button_sref
                                                                        }, countdown = 0,)

        # Push an invite out to the target user via socket server
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        push_payload = {'senderKeyId': str(authorized_user.key.id()), 'senderUserTitle': authorized_user.title}

        payload_json = json.dumps(push_payload)

        #try:
        URL = "%s/user/%s/friend/invite/send" % (HEROKU_SOCKETIO_SERVER, target_user.firebaseUser)
        resp, content = http_auth.request(URL,
                                ##"PATCH",
                              "PUT", ## Write or replace data to a defined path,
                              payload_json,
                              headers=headers)

        logging.info(resp)
        logging.info(content)

        #start tasks to update the friendlists
        taskUrl='/task/user/friends/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id(), 'online': True}, countdown = 2,)

        taskUrl='/task/user/friends/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': target_user.key.id()}, countdown = 2,)

        return UserRelationshipGetResponse(key_id = relationship.key.id(),
            userTargetKeyId = relationship.userTargetKeyId,
            userTargetKeyIdStr = str(relationship.userTargetKeyId),
            userTargetTitle = relationship.userTargetTitle,
            friend = relationship.friend,
            friendConfirmed = relationship.friendConfirmed,
            ignore = relationship.ignore,
            nickname = relationship.nickname,
            response_message='Success.',
            response_successful = True,
            relationship_exists = True,
            updated = update)


    @endpoints.method(USER_RELATIONSHIP_CREATE_RESOURCE, UserRelationshipGetResponse, path='invitationResponse', http_method='POST', name='invitation.response')
    def invitationResponse(self, request):
        """
        When a user responds to a friend invite, they accept or reject it.
        The difference between this and edit, is that a rejected invitation is deleted.
        """
        logging.info("invitationResponse")

        urController = UserRelationshipsController()
        uController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserRelationshipGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserRelationshipGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))

        ## get initiating user
        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            logging.error('authorized_user not found')
            return UserRelationshipGetResponse(response_message='Error: User Record Missing.', response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))

        ## self target
        if authorized_user.key.id() == int(request.key_id):
            logging.error('You cannot add yourself to the friends list')
            return UserRelationshipGetResponse(response_message='Error: You cannot add yourself to the friends list.', response_successful=False,
                                                    userTargetKeyId = request.key_id,
                                                    userTargetKeyIdStr = str(request.key_id))

        ## get target
        target_user = uController.get_by_key_id(int(request.key_id))
        if not target_user:
            logging.error('target_user not found')
            return UserRelationshipGetResponse(response_message='Error: Could not get target from key.',  response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))

        ## check if relationship already exists
        existing_relationship = urController.get_by_userKeyId_userTargetKeyId(authorized_user.key.id(), target_user.key.id())

        update = False

        if existing_relationship:
            if existing_relationship.friend:
                logging.info('Relationship already exists.')
                return UserRelationshipGetResponse(response_message='Error: Relationship already exists.', response_successful=False,
                                                    userTargetKeyId = request.key_id,
                                                    userTargetKeyIdStr = str(request.key_id))
            else:
                update = True


        ## check if there is a corresponding friend
        corresponding_relationship = urController.get_by_userKeyId_userTargetKeyId( target_user.key.id(), authorized_user.key.id())

        friendConfirmed = False

        acceptFriendRequest = request.friend

        if corresponding_relationship:
            if corresponding_relationship.friend:
                if acceptFriendRequest:
                    logging.info('Accepting the invite')
                    friendConfirmed = True
                    corresponding_relationship.friendConfirmed = True
                    urController.update(corresponding_relationship)
                else:
                    logging.info('rejecting the invite')
                    ## delete it!
                    urController.delete(corresponding_relationship)

                    ## TODO achievements

                    # Just return so we skip the new relationship record
                    return UserRelationshipGetResponse(response_message='Success.  Rejected the invite.', response_successful=True,
                                                        userTargetKeyId = request.key_id,
                                                        userTargetKeyIdStr = str(request.key_id))
            else:
                logging.info('Corresponding Relationship friend = false.')
                return UserRelationshipGetResponse(response_message='Error: Corresponding Relationship friend = false.', response_successful=False,
                                                    userTargetKeyId = request.key_id,
                                                    userTargetKeyIdStr = str(request.key_id))
        else:
            logging.info('Corresponding Relationship not found.')
            return UserRelationshipGetResponse(response_message='Error: Corresponding Relationship not found.', response_successful=False,
                                                userTargetKeyId = request.key_id,
                                                userTargetKeyIdStr = str(request.key_id))


        if update:
            existing_relationship.friend = request.friend
            existing_relationship.friendConfirmed = friendConfirmed
            existing_relationship.ignore = request.ignore
            existing_relationship.nickname = request.nickname
            urController.update(existing_relationship)
            relationship = existing_relationship
        else:
            ## add the relationship
            relationship = urController.create(
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                userFirebaseUser = authorized_user.firebaseUser,
                userTargetKeyId = target_user.key.id(),
                userTargetTitle = target_user.title,
                userTargetFirebaseUser = target_user.firebaseUser,
                userTargetPicture = target_user.picture,
                friend = request.friend,
                friendConfirmed = friendConfirmed,
                ignore = request.ignore,
                nickname = request.nickname,
                online = target_user.online
            )

        ## Sense
        """
        SenseController().create(
            target_type = 'User',
            target_key = user.key.id(),
            target_title = user.title,
            ref_type = 'User',
            ref_key = target_user.key.id(),
            action = 'Friend Added',
            title = '%s Added a Friend %s' % (user.title, target_user.title),
            description = '%s Added a Friend %s' % (user.title, target_user.title),
            ##amount = request.amount
        )
        """
        if friendConfirmed:
            description = "%s is now your friend" %(authorized_user.title)

            # send an alert to the target user
            ## push an alert out to firebase
            taskUrl='/task/user/alert/create'
            action_button_sref = '#/user/' + str(authorized_user.key.id())
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': target_user.firebaseUser,
                                                                            'material_icon': MATERIAL_ICON_FRIENDS,
                                                                            'importance': 'md-primary',
                                                                            ## TODO this message can be more helpful
                                                                            'message_text': description,
                                                                            'action_button_color': 'primary',
                                                                            'action_button_sref': action_button_sref
                                                                            }, countdown = 0,)

        # Push an invite out to the target user via socket server?


        #start tasks to update the friendlists
        taskUrl='/task/user/friends/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id(), 'online': True}, countdown = 2,)

        taskUrl='/task/user/friends/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': target_user.key.id()}, countdown = 2,)

        return UserRelationshipGetResponse(key_id = relationship.key.id(),
            userTargetKeyId = relationship.userTargetKeyId,
            userTargetKeyIdStr = str(relationship.userTargetKeyId),
            userTargetTitle = relationship.userTargetTitle,
            friend = relationship.friend,
            friendConfirmed = relationship.friendConfirmed,
            ignore = relationship.ignore,
            nickname = relationship.nickname,
            response_message='Success.',
            response_successful = True,
            relationship_exists = True,
            updated = update)


    @endpoints.method(USER_RELATIONSHIP_CREATE_RESOURCE, UserRelationshipGetResponse, path='edit', http_method='POST', name='edit')
    def edit(self, request):
        """ Update a user relationship """
        logging.info("userRelationshipEdit")

        urController = UserRelationshipsController()
        uController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserRelationshipGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserRelationshipGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        ## get initiating user
        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            return UserRelationshipGetResponse(response_message='Error: User Record Missing.', response_successful=False)


        ## self target
        if authorized_user.key.id() == request.key_id:
             return UserRelationshipGetResponse(response_message='Error: You cannot add yourself to the friends list.', response_successful=False)

        ## get target
        target_user = uController.get_by_key_id(request.key_id)
        if not target_user:
            return UserRelationshipGetResponse(response_message='Error: Could not get target from key.', response_successful=False)



        ## check if relationship already exists
        logging.info(authorized_user.key.id())
        logging.info(target_user.key.id())
        existing_relationship = urController.get_by_userKeyId_userTargetKeyId(authorized_user.key.id(), target_user.key.id())

        if not existing_relationship:
            logging.info('relationship not found')
            return UserRelationshipGetResponse(response_message='Error: Relationship does not exist.', response_successful=False)


        ## check if there is a corresponding friend
        corresponding_relationship = urController.get_by_userKeyId_userTargetKeyId( target_user.key.id(), authorized_user.key.id())

        friendConfirmed = False
        corresponding_changed = False
        ## what is the user doing?
        if request.friend:
            logging.info('friending')
            # friending, check coresponding friend, set confirmed
            if corresponding_relationship:
                if corresponding_relationship.friend:
                    friendConfirmed = True
                    corresponding_relationship.friendConfirmed = True
                    corresponding_changed = True
        else:
            logging.info('UN-friending')
            ##  unfriending, check the corresponding friend, unset confirmed
            if corresponding_relationship:
                logging.info('updating corresponding relationship')
                if corresponding_relationship.friend:
                    friendConfirmed = False
                    corresponding_relationship.friendConfirmed = False
                    corresponding_changed = True

        if corresponding_changed:
            urController.update(corresponding_relationship)

        ## update the relationship

        existing_relationship.friend = request.friend
        existing_relationship.friendConfirmed = friendConfirmed
        existing_relationship.ignore = request.ignore
        if request.nickname:
            existing_relationship.nickname = request.nickname

        urController.update(existing_relationship)

        return UserRelationshipGetResponse(key_id = existing_relationship.key.id(),
            userTargetKeyId = existing_relationship.userTargetKeyId,
            userTargetTitle = existing_relationship.userTargetTitle,
            friend = existing_relationship.friend,
            friendConfirmed = existing_relationship.friendConfirmed,
            ignore = existing_relationship.ignore,
            nickname = existing_relationship.nickname,
            response_message='Success.',
            response_successful=True,
            relationship_exists=True)


    @endpoints.method(USER_RELATIONSHIPS_COLLECTION_PAGE_RESOURCE, UserRelationshipCollectionOSS, path='collectionGet', http_method='POST', name='collection.get')
    def collectionGet(self, request):
        """ Get a collection of user relationships """
        logging.info("userRelationshipCollectionGet")

        ## this is used by the Unreal engine online subsystem to query a frieend list after the login flow is complete.

        ## if we have a gameKeyId, use it to check if the friend is playing the same game


        urController = UserRelationshipsController()
        uController = UsersController()
        if not self.request_state.headers['x-uetopia-auth']:
            logging.error('Firebase Unauth')
            return UserRelationshipCollectionOSS(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserRelationshipCollectionOSS(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserRelationshipCollectionOSS(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        ## get initiating user
        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            logging.error('authorized_user not found')
            return UserRelationshipCollectionOSS(response_message='Error: User Record Missing.', response_successful=False)

        gameKeyId = request.gameKeyId
        if gameKeyId:
            logging.info('found gameKeyId')
            gameKeyId = int(gameKeyId)



        #curs = Cursor(urlsafe=request.cursor)
        #sort_order = request.sort_order
        #direction = request.direction

        relationships = urController.get_by_userKeyId(authorized_user.key.id())
        datalist = []

        for relationship in relationships:
            logging.info('found relationship: %s' %relationship.userTargetTitle)
            if relationship.playingGameKeyId:
                if relationship.playingGameKeyId == gameKeyId:
                    ## friend is playing the same game
                    bIsPlayingThisGame = True
                else:
                    ## friend is not playing the same game.
                    bIsPlayingThisGame = False
            else:
                ## friend is not playing the same game.
                bIsPlayingThisGame = False

            datalist.append(UserRelationshipGetResponseOSS(
                key_id = relationship.userTargetKeyId,
                keyIdStr = str(relationship.userTargetKeyId),
                ##userTargetKeyId = relationship.userTargetKeyId,
                ##userTargetTitle = relationship.userTargetTitle,
                friend = relationship.friend,
                friendConfirmed = relationship.friendConfirmed,
                ignore = relationship.ignore,
                username = relationship.userTargetTitle,
                bIsOnline = relationship.online,
                bIsPlayingThisGame = bIsPlayingThisGame,
            ))

        response = UserRelationshipCollectionOSS(
            data = datalist
        )

        return response

    @endpoints.method(USER_RELATIONSHIPS_COLLECTION_PAGE_RESOURCE, UserRelationshipCollectionOSS, path='recentPlayerCollectionGet', http_method='POST', name='recent.collection.get')
    def recentPlayerCollectionGet(self, request):
        """ Get a collection of recent players """
        logging.info("recentPlayerCollectionGet")

        ## this is used by the Unreal engine online subsystem to query for users that have been played with recently.

        ## if we have a gameKeyId, use it to check if the friend is playing the same game


        urController = UserRelationshipsController()
        uController = UsersController()
        if not self.request_state.headers['x-uetopia-auth']:
            logging.error('Firebase Unauth')
            return UserRelationshipCollectionOSS(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserRelationshipCollectionOSS(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserRelationshipCollectionOSS(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        ## get initiating user
        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            return UserRelationshipCollectionOSS(response_message='Error: User Record Missing.', response_successful=False)

        gameKeyId = request.gameKeyId
        if gameKeyId:
            logging.info('found gameKeyId')
            gameKeyId = int(gameKeyId)

        matchPlayerController = MatchPlayersController()

        ## get the matches that this user has been in recently  - limit is set to 3
        this_users_recent_matches = matchPlayerController.get_recent_by_userKeyId(authorized_user.key.id())

        idlist = []
        datalist = []

        ## get the opponents of these matches
        for this_user_match in this_users_recent_matches:
            this_match_opponents = matchPlayerController.get_opponents_by_matchKeyId_userKeyId(this_user_match.matchKeyId, authorized_user.key.id())

            ## add any non-duplicates to the datalist.
            for this_match_opponent in this_match_opponents:
                if this_match_opponent.userKeyId not in idlist:
                    idlist.append(this_match_opponent.userKeyId)
                    datalist.append(UserRelationshipGetResponseOSS(
                        key_id = this_match_opponent.userKeyId,
                        keyIdStr = str(this_match_opponent.userKeyId),
                        ##userTargetKeyId = relationship.userTargetKeyId,
                        ##userTargetTitle = relationship.userTargetTitle,
                        #friend = relationship.friend,
                        #friendConfirmed = relationship.friendConfirmed,
                        #ignore = relationship.ignore,
                        username = this_match_opponent.userTitle,
                        #bIsOnline = relationship.online,
                        #bIsPlayingThisGame = bIsPlayingThisGame,
                        )
                    )

        response = UserRelationshipCollectionOSS(
            data = datalist
        )

        return response

    @endpoints.method(USER_RELATIONSHIP_CREATE_RESOURCE, UserRelationshipGetResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a user relationship """
        logging.info("userRelationshipGet")

        urController = UserRelationshipsController()
        uController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return UserRelationshipGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return UserRelationshipGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        ## get initiating user
        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            return UserRelationshipGetResponse(response_message='Error: User Record Missing.', response_successful=False)


        ## self target
        if authorized_user.key.id() == request.key_id:
             return UserRelationshipGetResponse(response_message='Error: You cannot be friends with yourself.  How sad.', response_successful=False)

        ## get target
        target_user = uController.get_by_key_id(request.key_id)
        if not target_user:
            return UserRelationshipGetResponse(response_message='Error: Could not get target from key.', response_successful=False,
                relationship_exists=False)



        ## check if relationship already exists
        logging.info(authorized_user.key.id())
        logging.info(target_user.key.id())
        existing_relationship = urController.get_by_userKeyId_userTargetKeyId(authorized_user.key.id(), target_user.key.id())

        if not existing_relationship:
            logging.info('relationship not found')
            return UserRelationshipGetResponse(response_message='Error: Relationship does not exist.',
                                                    friend=False,
                                                    friendConfirmed=False,
                                                    ignore=False,
                                                    response_successful=True,
                                                    relationship_exists=False)

        response = UserRelationshipGetResponse(
            key_id = existing_relationship.key.id(),
            userTargetKeyId = existing_relationship.userTargetKeyId,
            userTargetTitle = existing_relationship.userTargetTitle,
            friend = existing_relationship.friend,
            friendConfirmed = existing_relationship.friendConfirmed,
            ignore = existing_relationship.ignore,
            nickname = existing_relationship.nickname,
            response_successful=True,
            relationship_exists = True
        )

        return response
