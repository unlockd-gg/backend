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
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.game_players import GamePlayersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.models.chat_messages import *
from apps.uetopia.models.chat_channels import *
from apps.uetopia.models.chat_channel_subscribers import *


from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="chat", version="v1", description="Chat API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class ChatApi(remote.Service):
    @endpoints.method(CHAT_MESSAGE_CREATE_RESOURCE, ChatMessageGetResponse, path='messageCreate', http_method='POST', name='message.create')
    def messageCreate(self, request):
        """ Create a chat message """
        logging.info("chatMessageCreate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ChatMessageGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return ChatMessageGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ChatMessageGetResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gameController = GamesController()
        gpController = GamePlayersController()

        chat_channel_controller = ChatChannelsController()
        chat_channel_subscriber_controller = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        ## This request could be a personal message, where we would have a userKeyId
        ## Or, it could be a chat channel message, where we have a chatChannelKeyId

        userKeyId = request.userKeyId
        if userKeyId:
            logging.info("this is a personal message.")

            target_user = UsersController().get_by_key_id(userKeyId)
            ## TODO - implement this

        else:


            try:
                ## Check if this channel exists
                chat_channel = chat_channel_controller.get_by_key_id(int(request.chatChannelKeyId))

                if not chat_channel:
                    logging.error('Error:  Chat Channel could not be found with the supplied request.chatChannelKeyId) %s' %request.chatChannelKeyId)
                    return ChatMessageGetResponse(response_message='Error:  Chat Channel could not be found with the supplied key ', response_successful=False)
            except:
                logging.error('Error:  Chat Channel could not be found with the supplied request.chatChannelKeyId) %s' %request.chatChannelKeyId)
                return ChatMessageGetResponse(response_message='Error:  Chat Channel could not be found with the supplied key ', response_successful=False)

            ## check to see if the user is subscribed

            chat_channel_subscriber = chat_channel_subscriber_controller.get_by_channel_and_user(int(request.chatChannelKeyId), authorized_user.key.id())

            if not chat_channel_subscriber:
                return ChatMessageGetResponse(response_message='Error:  You are not subscribed to this channel ', response_successful=False)

            logging.info("channel_id: %s"%request.channel_id)

            ## convert any incoming commands

            if len(request.text) > 1:
                logging.info('message size ok')

                if request.text[0] == '/':
                    logging.info('slash command found')

                    """

                    ## WE need to ditch the chat_channel the user posted to
                    ##  and switch to the user's channel
                    ## TODO make a task that will only do a push to this player for command responses

                    player_chat_channel = chat_channel_controller.get_by_refKey(player.key.urlsafe())

                    ## strip it off
                    command = request.text[1:]
                    logging.info(command)
                    ## split the string
                    command_list = command.split()



                    ## look up the command
                    if command_list[0] in LEET_CHAT_COMMAND_LIST:
                        logging.info('Found command path')

                        ## execute task to perform indicated action.

                        ## TODO refactor this

                        if command_list[0] == "create":
                            chat_command_create(player_chat_channel, player, command)
                        elif command_list[0] == "join":
                            chat_command_join(player_chat_channel, player, command)
                        elif command_list[0] == "help":
                            chat_command_help(player_chat_channel, player, command)
                        elif command_list[0] == "resetui":
                            chat_command_resetui(player_chat_channel, player, command, request.channel_id)
                    else:
                        taskUrl='/task/channel/chat/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key': player_chat_channel.key.urlsafe(),
                                                                                            "message": "could not execute command: %s  try /help"%command_list[0]
                                                                                        })
                    """

                else:

                    chat_created = False

                    ## TODO check to see if we should be using a characterTitle
                    if chat_channel.gameKeyId:
                        logging.info('checking game for character enabled')

                        game = gameController.get_by_key_id(chat_channel.gameKeyId)

                        if game:
                            logging.info('got game')

                            game_player = gpController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())

                            if game.characters_enabled:
                                logging.info('characters enabled')

                                ## add the message to the database
                                chat_message = chat_message_controller.create(
                                    chatChannelKeyId = chat_channel.key.id(),
                                    chatChannelTitle = chat_channel.title,
                                    userKeyId = authorized_user.key.id(),
                                    userTitle = game_player.characterCurrentTitle,
                                    text = request.text,
                                    #pulled = False
                                )

                                chat_created = True

                                taskUrl='/task/chat/channel/send'
                                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': chat_channel.key.id(),
                                                                                                    "message": request.text,
                                                                                                    "userKeyId": authorized_user.key.id(),
                                                                                                    "userTitle": game_player.characterCurrentTitle,
                                                                                                    "chatMessageKeyId": chat_message.key.id(),
                                                                                                    "chatChannelTitle": chat_channel.title,
                                                                                                    "chatChannelRefType":chat_channel.channel_type,
                                                                                                    "created":chat_message.created.isoformat()
                                                                                                })



                    if not chat_created:
                        ## add the message to the database
                        chat_message = chat_message_controller.create(
                            chatChannelKeyId = chat_channel.key.id(),
                            chatChannelTitle = chat_channel.title,
                            userKeyId = authorized_user.key.id(),
                            userTitle = authorized_user.title,
                            text = request.text,
                            #pulled = False
                        )

                        taskUrl='/task/chat/channel/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': chat_channel.key.id(),
                                                                                            "message": request.text,
                                                                                            "userKeyId": authorized_user.key.id(),
                                                                                            "userTitle": authorized_user.title,
                                                                                            "chatMessageKeyId": chat_message.key.id(),
                                                                                            "chatChannelTitle": chat_channel.title,
                                                                                            "chatChannelRefType":chat_channel.channel_type,
                                                                                            "created":chat_message.created.isoformat()
                                                                                        })

        return ChatMessageGetResponse(response_message='Success', response_successful=True)

    @endpoints.method(CHAT_CHANNEL_CREATE_RESOURCE, ChatChanelGetResponse, path='channelCreate', http_method='POST', name='channel.create')
    def channelCreate(self, request):
        """ Create a chat channel """
        logging.info("chatChannelCreate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ChatChanelGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return ChatChanelGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ChatChanelGetResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ccController = ChatChannelsController()


        chat_channel_list_owner = ccController.get_all_by_adminUserKeyId(authorized_user.key.id())

        if len(chat_channel_list_owner) >10:
            logging.info('Error: You cannot own more than 10 chat channels.')

            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                                "message": 'Error: You cannot own more than 10 chat channels.',
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })

            return ChatChanelGetResponse(response_message='Error: You cannot own more than 10 chat channels.', response_successful=False)

        ## make sure there is no custom channel with this name
        existing_channel = ccController.get_custom_by_title(request.title)
        if existing_channel:
            chat_message = "> Chat Channel %s already exists.  You can create a new channel using a different title, or join this one." % request.title
            taskUrl='/task/chat/send'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': authorized_user.firebaseUser,
                                                                                "message": chat_message,
                                                                                "created":datetime.datetime.now().isoformat()
                                                                            })
            return ChatChanelGetResponse(key_id = chat_channel.key.id(),
                                response_message= chat_message,
                                response_successful=False)

        chat_channel = ChatChannelsController().create(
            title = request.title,
            #text_enabled = True,
            #data_enabled = False,
            channel_type = 'custom',
            adminUserKeyId = authorized_user.key.id(),
            refKeyId = None,
            max_subscribers = 20
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
            chatChannelRefKeyId = None,
            channel_type = 'custom',
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

        """

        ## check achievement
        taskUrl='/task/player/achievement'
        taskqueue.add(url=taskUrl, queue_name='taskPlayerAchievement', params={'key': player.key.urlsafe(),
                                                                                "code": "chatchannelcreate",
                                                                                "count": len(chat_channel_list_owner) +1
                                                                            }, countdown=2)


        ## Sense
        SenseController().create(
            target_type = 'Player',
            target_key = player.key.urlsafe(),
            target_title = player.title,
            ref_type = 'Chat Channel',
            ref_key = chat_channel.key.urlsafe(),
            action = 'Created Chat Channel',
            title = '%s Created a Chat Channel' % player.title,
            description = '%s Created a Chat Channel' % player.title,
            ##amount = request.wager
        )
        """

        return ChatChanelGetResponse(key_id = chat_channel.key.id(),
                            response_message= "Success.  Channel Created.",
                            response_successful=True,
                            max_subscribers = chat_channel.max_subscribers)



    @endpoints.method(CHAT_CHANNEL_CONNECT_RESOURCE, ChatChanelGetResponse, path='channelConnect', http_method='POST', name='channel.connect')
    def channelConnect(self, request):
        """ Connect to a chat channel """
        logging.info("channelConnect")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ChatChanelGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return ChatChanelGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ChatChanelGetResponse(response_message='Error: No User Record Found. ', response_successful=False)


        ccController = ChatChannelsController()
        chat_subscriber_controller = ChatChannelSubscribersController()

        logging.info('request.title: %s'%request.title)
        chat_channel = ChatChannelsController().get_custom_by_title(request.title)
        if not chat_channel:
            logging.info('Error: Chat Channel not found')
            return ChatChanelGetResponse(response_message='Error: Chat Channel not found.', response_successful=False)

        ## check to see if the player is already connected

        chat_subscriber = chat_subscriber_controller.get_by_channel_and_user(chat_channel.key.id(), authorized_user.key.id())
        if not chat_subscriber:
            logging.info('subscribing player to channel')
            ## Subscribe the player to it
            subscriber = chat_subscriber_controller.create(
                online = True,
                chatChannelKeyId = chat_channel.key.id(),
                chatChannelTitle = chat_channel.title,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                userFirebaseUser = authorized_user.firebaseUser,
                post_count = 0,
                chatChannelRefKeyId = chat_channel.refKeyId,
                chatChannelOwnerKeyId = chat_channel.adminUserKeyId,
                channel_type = chat_channel.channel_type
            )
        else:
            logging.info('player already connected to this channel')

        ##  pushes

        chat_message = "> Joined Chat Channel %s " % chat_channel.title

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

        """

        ## send the user the updated chat channels
        taskUrl='/task/channel/send'
        taskqueue.add(url=taskUrl, queue_name='channelChatSend', params={'key': player.key.urlsafe()}, countdown = 2,)

        ## Fire off a task to send the channel data push

        if chat_channel.channel_type == "match":
            taskUrl='/task/match/push'
            taskqueue.add(url=taskUrl, queue_name='matchmakerPush', params={'key': chat_channel.refKey}, countdown = 2,)

        if chat_channel.channel_type == "server":
            taskUrl='/task/server/push'
            taskqueue.add(url=taskUrl, queue_name='serverPush', params={'key': chat_channel.refKey}, countdown = 2,)

        if chat_channel.channel_type == "player":
            taskUrl='/task/player/push'
            taskqueue.add(url=taskUrl, queue_name='playerPush', params={'key': chat_channel.refKey}, countdown = 2,)

        if chat_channel.channel_type == "group":
            taskUrl='/task/group/push'
            taskqueue.add(url=taskUrl, queue_name='groupPush', params={'key': chat_channel.refKey}, countdown = 2,)

        """

        return ChatChanelGetResponse(key_id = chat_channel.key.id(),
                            max_subscribers = chat_channel.max_subscribers,
                            response_message='Success.  Subscribed to channel.', response_successful=True)

    @endpoints.method(CHAT_CHANNEL_CONNECT_RESOURCE, ChatChanelGetResponse, path='channelDetach', http_method='POST', name='channel.detach')
    def channelDetach(self, request):
        """ Detach from a chat channel """
        logging.info("channelDetach")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ChatChanelGetResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return ChatChanelGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ChatChanelGetResponse(response_message='Error: No User Record Found. ', response_successful=False)


        ccController = ChatChannelsController()
        chat_subscriber_controller = ChatChannelSubscribersController()

        logging.info('request.key_id: %s'%request.key_id)
        chat_channel = ChatChannelsController().get_by_key_id(int(request.key_id))
        if chat_channel:
            #return ChatChanelGetResponse(response_message='Error: Chat Channel not found.', response_successful=False)

            ## TODO prevent players from leaving match and tournament chats if they are still active in them

            ##  prevent leaving group channels
            if chat_channel.channel_type == 'group':
                logging.info('Error:  Leave the group to leave group chat')
                return ChatChanelGetResponse(response_message='Error: Leave the group to leave group chat.', response_successful=False)

        ## check to see if the player is already connected

        chat_subscriber = chat_subscriber_controller.get_by_channel_and_user(int(request.key_id), authorized_user.key.id())
        if chat_subscriber:
            logging.info('user is subscribed')

            ## check to see if the player is the channel admin.
            ## If they are, check to see if there are any other subscribers
            ## If so, assign admin to one of them
            if chat_channel:
                if chat_channel.adminUserKeyId == authorized_user.key.id():
                    logging.info('user is the channel admin')

                    all_channel_subscribers = chat_subscriber_controller.get_by_chatChannelKeyId(int(request.key_id))
                    if len(all_channel_subscribers) == 1:
                        logging.info('user is the only subscriber')
                        ## just delete it
                        ccController.delete(chat_channel)
                    else:
                        logging.info('there are other users in this channel')
                        ## assign someone else
                        for i_channel_subscriber in all_channel_subscribers:
                            if i_channel_subscriber.userKeyId != authorized_user.key.id():
                                chat_channel.adminUserKeyId = i_channel_subscriber.userKeyId
                                ccController.update(chat_channel)
                                break
                        ## TODO fire off a randomized task to try to delete the chat channel
                        ## this is just in case two players leave at the exact same time.

            ChatChannelSubscribersController().delete(chat_subscriber)

            ## send the user the updated chat channels
            #taskUrl='/task/channel/send'
            #taskqueue.add(url=taskUrl, queue_name='channelChatSend', params={'key': player.key.urlsafe()})

            chat_message = "> Left Chat Channel %s " % chat_subscriber.chatChannelTitle

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

            message = "Success.  Disconnected."
            return ChatChanelGetResponse(response_message=message, response_successful=True)

        else:
            logging.info('player not connected to this channel')

            message = "You are not connected to this channel."
            return ChatChanelGetResponse(response_message=message, response_successful=False)


    @endpoints.method(message_types.VoidMessage, ChatChannelSubscriberCollection, path='channelSubscriberCollection', http_method='POST', name='subscribtion.collection')
    def channelSubscriberCollection(self, request):
        """ Get a list of chat channel subscribers """
        logging.info("channelSubscriberCollection")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ChatChannelSubscriberCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return ChatChanelGetResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ChatChanelGetResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ccController = ChatChannelsController()
        ccsController = ChatChannelSubscribersController()

        subscribers = ccsController.get_by_user(authorized_user.key.id())

        subscriberlist = []
        for i in subscribers:
            subscriberlist.append(ChatChanelSubscriberGetResponse(
                key_id = i.key.id(),
                key_id_str = str(i.key.id()),
                online = i.online,
                chatChannelKeyId = i.chatChannelKeyId,
                chatChannelKeyIdStr = str(i.chatChannelKeyId),
                chatChannelTitle = i.chatChannelTitle,
                post_count = i.post_count,
                chatChannelRefKeyId = i.chatChannelRefKeyId,
                chatChannelRefKeyIdStr = str(i.chatChannelRefKeyId),
                chatChannelOwnerKeyIdStr = str(i.chatChannelOwnerKeyId),
                chatChannelOwnerKeyId = i.chatChannelOwnerKeyId,
                channel_type = i.channel_type
            ))

        logging.info(subscriberlist)

        response = ChatChannelSubscriberCollection(
            chat_channel_subscribers = subscriberlist,
            response_message = "Success.", response_successful=True
        )

        return response
