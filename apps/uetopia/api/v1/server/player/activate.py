import logging
import datetime
import string
import json
import uuid
from httplib2 import Http
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_shards import ServerShardsController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_characters import GameCharactersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController

from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ActivatePlayerHandler(BaseHandler):
    def post(self, userid):
        """
        Check if user can be activated
        Requires http headers:  Key, Sign
        Requires POST parameters: nonce, access_token

        ## we don't actually need the userID anymore, we can get it all from authToken
        """

        serverController = ServersController()
        uController = UsersController()
        spController = ServerPlayersController()
        serverClusterController = ServerClustersController()
        serverShardController = ServerShardsController()
        serverShardPlaceholderController = ServerShardPlaceholderController()
        #cController = CurrencyController()
        gpController = GamePlayersController()
        lockController = TransactionLockController()
        transactionController = TransactionsController()

        chatChannelSubscribersController = ChatChannelSubscribersController()
        chatChannelController = ChatChannelsController()

        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()

        teamController = TeamsController()
        teamMemberController = TeamMembersController()
        gameCharacterController = GameCharactersController()



        server = serverController.verify_signed_auth(self.request)

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('server auth success')

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

                logging.info("incoming_userid: %s" % user.key.id())
                logging.info("serverKey: %s" % server.key.urlsafe())
                logging.info("serverKeyId: %s" % server.key.id())

                authorized = False
                activated = False
                previously_active = False
                user_key_id = user.key.id()
                player_name = None
                player_currency = 0
                player_rank = 1600
                auth_deny_reason = "None"
                player_userid = userid ## passed in via URL
                game_player_key_id = None

                ## grab the game so we can populate the active user feed
                game = GamesController().get_by_key_id(server.gameKeyId)

                # grab this user's game user Key
                game_player = gpController.get_by_gameKeyId_userKeyId(server.gameKeyId, user.key.id())
                if game_player:
                    logging.info('found existing game player')
                    game_player_key_id = game_player.key.id()
                else:
                    logging.info("Game player NOT found.")

                    ## it's safe to just create it.
                    ## assign a random server cluster
                    selected_server_cluster = serverClusterController.get_by_gameKeyId(game.key.id())
                    lastServerClusterKeyId = selected_server_cluster.key.id()

                    game_player = gpController.create(
                        gameKeyId = game.key.id(),
                        gameTitle = game.title,
                        userKeyId = user.key.id(),
                        userTitle = user.title,
                        locked = False,
                        online = True,
                        rank = 1600,
                        score = 0,
                        #autoAuth = True,
                        #autoAuthThreshold = 100000,
                        autoTransfer = True,
                        firebaseUser = user.firebaseUser,
                        picture = user.picture,
                        lastServerClusterKeyId = lastServerClusterKeyId,
                        groupKeyId = user.groupTagKeyId,
                        groupTag = user.groupTag,
                        showGameOnProfile = True
                    )

                    game_player_key_id = game_player.key.id()

                ## make sure the game player has the required tags
                if server.requireBadgeTags:
                    player_has_all_tags = True
                    missing_tags = []
                    missingTagsTextMessage = "> You do not have the tags required to join this server.  You are missing: "
                    for tag in server.requireBadgeTags:
                        if not game_player.badgeTags:
                            missing_tags.append(tag)
                            missingTagsTextMessage = missingTagsTextMessage + tag + ", "
                            player_has_all_tags = False
                            continue
                        if tag not in game_player.badgeTags:
                            missing_tags.append(tag)
                            missingTagsTextMessage = missingTagsTextMessage + tag + ", "
                            player_has_all_tags = False
                            continue

                    if not player_has_all_tags:
                        logging.info('player is missing a required tag')

                        missingTagsTextMessage = missingTagsTextMessage + ".  Check the available game offers to acquire these tags."

                        chat_msg = json.dumps({"type":"chat",
                                                "textMessage":missingTagsTextMessage,
                                                "userKeyId": "SYSTEM",
                                                "userTitle": "SYSTEM",
                                                #"chatMessageKeyId": chatMessageKeyId,
                                                #"chatChannelTitle": channel.title,
                                                #"chatChannelKeyId": channel.key.id(),
                                                "created":datetime.datetime.now().isoformat()
                        })

                        # push out to in-game clients via heroku
                        # ignore if it's failing
                        try:
                            URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, user.firebaseUser)
                            resp, content = http_auth.request(URL,
                                                ##"PATCH",
                                              "PUT", ## Write or replace data to a defined path,
                                              chat_msg,
                                              headers=headers)

                            logging.info(resp)
                            logging.info(content)
                        except:
                            logging.error('heroku error')

                ## instanced and sharded servers require special handling for transactions
                ## they should not get the admission fee directly, it should go to the parent template .
                if server.instanced_from_template:
                    wallet_server_key_id = server.instanced_from_template_serverKeyId
                    wallet_server_title = server.instanced_from_template_serverTitle
                elif server.sharded_from_template:
                    wallet_server_key_id = server.sharded_from_template_serverKeyId
                    wallet_server_title = server.sharded_from_template_serverTitle
                else:
                    wallet_server_key_id = server.key.id()
                    wallet_server_title = server.title

                # check to see if this server is accessible to the player attempting to connect
                # Instanced servers have restrictions

                if server.instanced_from_template:
                    logging.info('this is an instanced / parallel server')
                    if server.instance_server_configuration == "user":
                        logging.info('this is a user instance')
                        if server.instanced_for_userKeyId != user.key.id():
                            logging.info("this is not the users instance.  denying")

                            ## TODO - any cleanup?

                            return self.render_json_response(
                                authorization = True,
                                player_authorized = False,
                                player_previously_active = False,
                                user_key_id = str(user.key.id()),
                                player_name = user.title,
                                player_currency = 0,
                                player_rank = 0,
                                player_userid = player_userid,
                                game_player_key_id = ""
                            )

                    elif server.instance_server_configuration == "party":
                        logging.info('this is a party instance')

                        ## get the team member
                        existing_team_member = teamMemberController.get_by_teamKeyId_userKeyId(server.instanced_for_partyKeyId, user.key.id())
                        if not existing_team_member:
                            logging.info('did not find a party member account.  denying')

                            ## TODO - any cleanup?

                            return self.render_json_response(
                                authorization = True,
                                player_authorized = False,
                                player_previously_active = False,
                                user_key_id = str(user.key.id()),
                                player_name = user.title,
                                player_currency = 0,
                                player_rank = 0,
                                player_userid = player_userid,
                                game_player_key_id = ""
                            )


                    elif server.instance_server_configuration == "group":
                        logging.info('this is a group instance')

                        existing_group_member = groupUserController.get_by_groupKeyId_userKeyId(server.instanced_for_groupKeyId, user.key.id())
                        if existing_group_member:
                            logging.info('found a group member')
                            existing_group_member_role = groupRoleController.get_by_key_id(existing_group_member.roleKeyId)
                            if existing_group_member_role:
                                logging.info('found a group role')
                                if not existing_group_member_role.join_group_server_instances:
                                    logging.info('user does not have join_group_server_instances permission - denying')
                                    ## TODO - any cleanup?

                                    return self.render_json_response(
                                        authorization = True,
                                        player_authorized = False,
                                        player_previously_active = False,
                                        user_key_id = str(user.key.id()),
                                        player_name = user.title,
                                        player_currency = 0,
                                        player_rank = 0,
                                        player_userid = player_userid,
                                        game_player_key_id = ""
                                    )
                            else:
                                logging.info('no group role found - denying')

                                ## TODO - any cleanup?

                                return self.render_json_response(
                                    authorization = True,
                                    player_authorized = False,
                                    player_previously_active = False,
                                    user_key_id = str(user.key.id()),
                                    player_name = user.title,
                                    player_currency = 0,
                                    player_rank = 0,
                                    player_userid = player_userid,
                                    game_player_key_id = ""
                                )

                        else:
                            logging.info('no group membership found - denying')

                            ## TODO - any cleanup?

                            return self.render_json_response(
                                authorization = True,
                                player_authorized = False,
                                player_previously_active = False,
                                user_key_id = str(user.key.id()),
                                player_name = user.title,
                                player_currency = 0,
                                player_rank = 0,
                                player_userid = player_userid,
                                game_player_key_id = ""
                            )

                ## Done with parallel/instanced stuff

                # check to see if there is a server user member record
                server_player = spController.get_server_user(server.key.id(), user.key.id() )

                if server_player:
                    logging.info('server_player found')

                    if server_player.banned:
                        logging.info('this player is banned')
                        ## TODO - push error to developer discord
                        authorized = False
                        auth_deny_reason = "Authorization: banned"

                    else:

                        if server_player.active:
                            previously_active = True

                        if server_player.pending_deauthorize:
                            logging.info('server_player Set to pending deauthorize')
                            auth_deny_reason = "Authorization: pending deathorize"

                        else:
                            logging.info('server_player is not pending deauthorize')

                            #if server_player.authorized:
                            #    logging.info('server_player is authorized')

                            if user.currencyBalance >= server.minimumCurrencyHold:
                                logging.info('user has enough currency to activate')
                                player_currency = user.currencyBalance

                                if server.admissionFee:
                                    logging.info('admissionFee is enabled')
                                    ## Handle admissions fee

                                    player_currency = user.currencyBalance - server.admissionFee

                                    ## calculate the uetopia rake
                                    uetopia_rake = int(server.admissionFee * UETOPIA_GROSS_PERCENTAGE_RAKE)
                                    logging.info("uetopia_rake: %s" % uetopia_rake)

                                    remaining_admission_fee_to_server = server.admissionFee - uetopia_rake
                                    logging.info("remaining_admission_fee_to_server: %s" % remaining_admission_fee_to_server)

                                    description = "Admission Fee from: %s" %user.title
                                    recipient_transaction = transactionController.create(
                                        amountInt = remaining_admission_fee_to_server,
                                        amountIntGross = server.admissionFee,
                                        ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                                        ##newBalance = ndb.FloatProperty(indexed=False) # for display
                                        description = description,
                                        ##userKeyId = authorized_user.key.id(),
                                        ##firebaseUser = authorized_user.firebaseUser,
                                        ##targetUserKeyId = ndb.IntegerProperty()
                                        serverKeyId = wallet_server_key_id,
                                        serverTitle = wallet_server_title,

                                        ##  transactions are batched and processed all at once.
                                        transactionType = "server",
                                        transactionClass = "admission fee",
                                        transactionSender = False,
                                        transactionRecipient = True,
                                        submitted = True,
                                        processed = False,
                                        materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                                        materialDisplayClass = "md-primary"
                                    )

                                    description = "Admission Fee joining: %s" %wallet_server_title

                                    ## transaction for the user
                                    transactionController.create(
                                        amountInt = -server.admissionFee,
                                        description = description,
                                        #serverKeyId = server.key.id(),
                                        #serverTitle = server.title,
                                        userKeyId = user.key.id(),
                                        firebaseUser = user.firebaseUser,

                                        transactionType = "user",
                                        transactionClass = "admission fee",
                                        transactionSender = True,
                                        transactionRecipient = False,
                                        recipientTransactionKeyId = recipient_transaction.key.id(),
                                        submitted = True,
                                        processed = False,
                                        materialIcon = MATERIAL_ICON_PURCHASE,
                                        materialDisplayClass = "md-accent"
                                    )

                                    server_player.admission_paid = True

                                    ## only start pushable tasks.  If they are not pushable, there is already a task running.
                                    pushable = lockController.pushable("server:%s"%wallet_server_key_id)
                                    if pushable:
                                        logging.info('server pushable')
                                        taskUrl='/task/server/transaction/process'
                                        taskqueue.add(url=taskUrl, queue_name='serverTransactionProcess', params={
                                                                                                                "key_id": wallet_server_key_id
                                                                                                            }, countdown=2)

                                    pushable = lockController.pushable("user:%s"%user.key.id())
                                    if pushable:
                                        logging.info('user pushable')
                                        taskUrl='/task/user/transaction/process'
                                        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                                "key_id": user.key.id()
                                                                                                            }, countdown=2)

                                    ## Transaction for uetopia rake - this is marked as processed - just recording it.
                                    description = "Admission Fee Percentage from: %s" %user.title
                                    recipient_transaction = transactionController.create(
                                        amountInt = uetopia_rake,
                                        description = description,
                                        serverKeyId = wallet_server_key_id,
                                        serverTitle = wallet_server_title,
                                        gameKeyId = server.gameKeyId,
                                        gameTitle = server.gameTitle,
                                        transactionType = "uetopia",
                                        transactionClass = "admission fee rake",
                                        transactionSender = False,
                                        transactionRecipient = True,
                                        submitted = True,
                                        processed = True,
                                        materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                                        materialDisplayClass = "md-primary"
                                    )

                                ## set return values
                                authorized = True
                                user_key_id = user.key.id()
                                ## use group tag if set
                                if user.groupTag:
                                    player_name = user.groupTag + " " + user.title
                                else:
                                    player_name = user.title

                                activated = True
                                player_rank = server_player.ladderRank

                                ## Update the server user member record
                                server_player.active = True
                                #server_player.authorized = True
                                server_player.pending_authorize = False
                                server_player.userTitle = player_name

                                logging.info('updating server player - TODO verify this is not a one second rule violation')

                                spController.update(server_player)

                            else:
                                logging.info('User Currency balance below minimum')
                                authorized = False
                                auth_deny_reason = "Currency balance below minimum"

                                ## push an alert out to firebase
                                taskUrl='/task/user/alert/create'
                                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': user.firebaseUser,
                                                                                                'material_icon': MATERIAL_ICON_AUTO_AUTH_FAILURE,
                                                                                                'importance': 'md-warn',
                                                                                                ## TODO this message can be more helpful
                                                                                                'message_text': 'Your currency balance was below the minimum',
                                                                                                'action_button_color': 'primary',
                                                                                                'action_button_sref': '#/user/transactions'
                                                                                                }, countdown = 0,)


                else:
                    logging.info('server_player not found')
                    ## server player not found
                    if user.currencyBalance >= server.minimumCurrencyHold:
                        logging.info('user has enough currency to activate')
                        player_currency = user.currencyBalance

                        if server.admissionFee:
                            logging.info('admissionFee is enabled')
                            ## Handle admissions fee
                            player_currency = user.currencyBalance - server.admissionFee

                            ## calculate the uetopia rake
                            uetopia_rake = int(server.admissionFee * UETOPIA_GROSS_PERCENTAGE_RAKE)
                            logging.info("uetopia_rake: %s" % uetopia_rake)

                            remaining_admission_fee_to_server = server.admissionFee - uetopia_rake
                            logging.info("remaining_admission_fee_to_server: %s" % remaining_admission_fee_to_server)

                            description = "Admission Fee from: %s" %user.title
                            recipient_transaction = transactionController.create(
                                amountInt = remaining_admission_fee_to_server,
                                amountIntGross = server.admissionFee,
                                ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                                ##newBalance = ndb.FloatProperty(indexed=False) # for display
                                description = description,
                                ##userKeyId = authorized_user.key.id(),
                                ##firebaseUser = authorized_user.firebaseUser,
                                ##targetUserKeyId = ndb.IntegerProperty()
                                serverKeyId = wallet_server_key_id,
                                serverTitle = wallet_server_title,

                                ##  transactions are batched and processed all at once.
                                transactionType = "server",
                                transactionClass = "admission fee",
                                transactionSender = False,
                                transactionRecipient = True,
                                submitted = True,
                                processed = False,
                                materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                                materialDisplayClass = "md-primary"
                            )

                            description = "Admission Fee joining: %s" %wallet_server_title

                            ## transaction for the user
                            transactionController.create(
                                amountInt = -server.admissionFee,
                                description = description,
                                #serverKeyId = server.key.id(),
                                #serverTitle = server.title,
                                userKeyId = user.key.id(),
                                firebaseUser = user.firebaseUser,

                                transactionType = "user",
                                transactionClass = "admission fee",
                                transactionSender = True,
                                transactionRecipient = False,
                                recipientTransactionKeyId = recipient_transaction.key.id(),
                                submitted = True,
                                processed = False,
                                materialIcon = MATERIAL_ICON_PURCHASE,
                                materialDisplayClass = "md-accent"
                            )



                            ## only start pushable tasks.  If they are not pushable, there is already a task running.
                            pushable = lockController.pushable("server:%s"%wallet_server_key_id)
                            if pushable:
                                logging.info('server pushable')
                                taskUrl='/task/server/transaction/process'
                                taskqueue.add(url=taskUrl, queue_name='serverTransactionProcess', params={
                                                                                                        "key_id": wallet_server_key_id
                                                                                                    }, countdown=2)

                            pushable = lockController.pushable("user:%s"%user.key.id())
                            if pushable:
                                logging.info('user pushable')
                                taskUrl='/task/user/transaction/process'
                                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                        "key_id": user.key.id()
                                                                                                    }, countdown=2)

                            ## Transaction for uetopia rake - this is marked as processed - just recording it.
                            description = "Admission Fee Percentage from: %s" %user.title
                            recipient_transaction = transactionController.create(
                                amountInt = uetopia_rake,
                                description = description,
                                serverKeyId = wallet_server_key_id,
                                serverTitle = wallet_server_title,
                                gameKeyId = server.gameKeyId,
                                gameTitle = server.gameTitle,
                                transactionType = "uetopia",
                                transactionClass = "admission fee rake",
                                transactionSender = False,
                                transactionRecipient = True,
                                submitted = True,
                                processed = True,
                                materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                                materialDisplayClass = "md-primary"
                            )

                        ## Create the server player

                        ## use group tag if set
                        if user.groupTag:
                            player_name = user.groupTag + " " + user.title
                        else:
                            player_name = user.title

                        ## Create the server user member
                        server_player = spController.create(
                            authTimestamp = datetime.datetime.now(),
                            authCount = 1,
                            deAuthCount = 0,
                            serverKeyId = server.key.id(),
                            serverTitle = server.title,
                            gameKeyId = server.gameKeyId,
                            gameTitle = game.title,
                            userKeyId = user.key.id(),
                            firebaseUser = user.firebaseUser,
                            #currencyStart = currency_hold,
                            #currencyCurrent = currency_hold - admission,
                            userTitle = player_name,
                            pending_authorize = False,
                            pending_deauthorize = False,
                            authorized = True,
                            active = True,
                            banned = False,
                            ladderRank = 1600,
                            experience = 0,
                            experience_total = 0,
                            admission_paid = True,
                            #internal_matchmaker = False,
                            #avatar_theme = user.avatar_theme
                        )

                        authorized = True

                    else:
                        ##  send a text chat

                        chatMessage =  "Could not join the server.  Your currency balance was below the minimum."

                        chat_msg = json.dumps({"type":"chat",
                                                "textMessage":chatMessage,
                                                "userKeyId": "SYSTEM",
                                                "userTitle": "SYSTEM",
                                                #"chatMessageKeyId": chatMessageKeyId,
                                                #"chatChannelTitle": channel.title,
                                                #"chatChannelKeyId": channel.key.id(),
                                                "created":datetime.datetime.now().isoformat()
                        })

                        # push out to in-game clients via heroku
                        # ignore if it's failing
                        try:
                            URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, user.firebaseUser)
                            resp, content = http_auth.request(URL,
                                                ##"PATCH",
                                              "PUT", ## Write or replace data to a defined path,
                                              chat_msg,
                                              headers=headers)

                            logging.info(resp)
                            logging.info(content)
                        except:
                            logging.error('heroku error')

                        ## push an alert out to firebase
                        taskUrl='/task/user/alert/create'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': user.firebaseUser,
                                                                                        'material_icon': MATERIAL_ICON_AUTO_AUTH_FAILURE,
                                                                                        'importance': 'md-warn',
                                                                                        ## TODO this message can be more helpful
                                                                                        'message_text': 'Your currency balance was below the minimum',
                                                                                        'action_button_color': 'primary',
                                                                                        'action_button_sref': '#/user/transactions'
                                                                                        }, countdown = 0,)

                logging.info("game_player_key_id: %s" %game_player_key_id)

                if authorized:
                    ##  update firebase server player record
                    taskUrl='/task/server/player/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id(), 'connecting': 'true', 'disconnecting': 'false'}, countdown = 2,)

                    taskUrl='/task/user/firebase/update'
                    playingLink = '/#/game/%s/server/%s'%(game.key.id(), server.key.id())
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                                    'playingGame': game.title,
                                                                                    'playingGameKeyId': game.key.id(),
                                                                                    'playingOnServer': server.title,
                                                                                    'playingOnServerKeyId': server.key.id(),
                                                                                    'playingLink': playingLink,
                                                                                    'online': True }, countdown = 2,)

                    ## kill off the checkUnusedTaskName task if it exists
                    if server.checkUnusedTaskName:
                        logging.info('killing off checkUnusedTaskName')

                        q = taskqueue.Queue('serverCheckUnused')
                        q.delete_tasks(taskqueue.Task(name=server.checkUnusedTaskName))
                        server.checkUnusedTaskName = None
                        serverController.update(server)

                    # make sure the player is subscribed to the server's chat channel
                    server_chat_channel = chatChannelController.get_by_channel_type_refKeyId('server', server.key.id())
                    if server_chat_channel:
                        existing_chat_subscriber = chatChannelSubscribersController.get_by_channel_and_user(server_chat_channel.key.id(), user.key.id())
                        if not existing_chat_subscriber:
                            new_chat_subscriber = chatChannelSubscribersController.create(
                                online = True,
                                chatChannelKeyId = server_chat_channel.key.id(),
                                chatChannelTitle = server_chat_channel.title,
                                userKeyId = user.key.id(),
                                userTitle = user.title,
                                userFirebaseUser = user.firebaseUser,
                                post_count = 0,
                                chatChannelRefKeyId = server.key.id(),
                                channel_type = 'server',
                                chatChannelOwnerKeyId = server.userKeyId
                            )

                        ## use guild tag if set
                        if user.groupTag:
                            chat_message = "%s " % user.groupTag
                        else:
                            chat_message = ""
                        ## use character title instead of user title if characters are enabled
                        if game.characters_enabled:
                            chat_message = chat_message + "%s joined" % game_player.characterCurrentTitle
                        else:
                            chat_message = chat_message + "%s joined" % user.title

                        # push chat channels

                        taskUrl='/task/chat/channel/list_changed'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                        'userKeyId': user.key.id(),
                                                                                        'textMessage': chat_message
                                                                                        }, countdown = 2)

                        taskUrl='/task/chat/channel/send'
                        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': server_chat_channel.key.id(),
                                                                                            "message": chat_message,
                                                                                            #"userKeyId": authorized_user.key.id(),
                                                                                            #"userTitle": authorized_user.title,
                                                                                            "chatMessageKeyId": uuid.uuid4(),
                                                                                            "chatChannelTitle": server_chat_channel.title,
                                                                                            "chatChannelRefType":server_chat_channel.channel_type,
                                                                                            "created":datetime.datetime.now().isoformat()
                                                                                        })

                        ##  also send out a chat informing the player if they have joined a sharded server
                        if server.sharded_from_template:
                            chat_message = "Joined a sharded server "
                            taskUrl='/task/chat/send'
                            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                                "message": chat_message,
                                                                                                "created":datetime.datetime.now().isoformat()
                                                                                            })

                        ## if the user is on a team/party, push an update.
                        ## get the team member
                        existing_team_member = teamMemberController.get_by_gameKeyId_userKeyId(server.gameKeyId, user.key.id())
                        if  existing_team_member:
                            logging.info('found a team member')

                            ## queue up the task to send a message to all team members
                            taskUrl='/task/team/firebase/update'
                            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': existing_team_member.teamKeyId}, countdown = 2,)


                    #taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                    #                                                                    "message": chat_message,
                    #                                                                    "created":datetime.datetime.now().isoformat()
                    #                                                                })

                    ## if it is a sharded server - update the connected player count
                    if server.sharded_from_template:
                        logging.info('found a shard')
                        s_shard = serverShardController.get_by_serverShardKeyId(server.key.id())
                        if s_shard:
                            logging.info('found the shard data')
                            ## look up the player count.  Could just increment here, but this is safer
                            server_shard_players = spController.get_list_authorized_by_server(server.key.id())
                            logging.info('found %s authorized players on this shard' % len(server_shard_players) )
                            s_shard.playerCount = len(server_shard_players)
                            serverShardController.update(s_shard)

                            ## also delete the placeholder if it exists
                            existing_placeholders = serverShardPlaceholderController.list_by_userKeyId( user.key.id() )
                            for existing_placeholder in existing_placeholders:
                                logging.info('deleting placeholder')
                                serverShardPlaceholderController.delete(existing_placeholder)




                taskUrl='/task/server/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server.key.id()}, countdown = 2,)

                ## Check the team/party and create one if it does not exist.

                existing_team_member = teamMemberController.get_by_gameKeyId_userKeyId(server.gameKeyId, user.key.id())
                if not existing_team_member:
                    logging.info('did not find a team member - creating')

                    ## create a new team, and team member.  We need it later.
                    if user.defaultTeamTitle:
                        title = user.defaultTeamTitle
                    else:
                        title = user.title + "'s Team"

                    team = teamController.create(
                        title = title,
                        description = "created via server player activate",
                        pug = False,
                        #teamAvatarTheme = player.avatar_theme,

                        gameKeyId = game.key.id(),
                        gameTitle = game.title,

                        #groupMembersOnly = False, ## TODO implement this?
                        #groupKey = request
                        #groupTitle = ndb.StringProperty()

                        captainPlayerKeyId = user.key.id(),
                        captainPlayerTitle = user.title,

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

                    if game.characters_enabled:
                        logging.info('characters are enabled.')
                        if game_player.characterCurrentKeyId:
                            logging.info('this game_player has a characterCurrentKeyId')
                            game_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
                            if not game_character:
                                logging.info('game character not found')
                                return self.render_json_response(
                                    authorization = True,
                                    response_successful = False,
                                    response_message = 'your character could not be found.'
                                )

                        else:
                            logging.info('You did not have a character selected.')
                            return self.render_json_response(
                                authorization = True,
                                response_successful = False,
                                response_message = 'You do not have an active character'
                            )


                    team_player = teamMemberController.create(
                        teamKeyId = team.key.id(),
                        teamTitle = team.title,
                        userKeyId = user.key.id(),
                        userTitle = user.title,
                        userFirebaseUser = user.firebaseUser,
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
                    party_chat_title = "%s chat" % title
                    party_chat_channel = chatChannelController.create(
                        title = party_chat_title,
                        channel_type = 'team',
                        #adminUserKeyId = user.key.id(),
                        refKeyId = team.key.id(),
                        gameKeyId = game.key.id(),
                        max_subscribers = 20
                    )

                    subscriber = chatChannelSubscribersController.create(
                        online = True,
                        chatChannelKeyId = party_chat_channel.key.id(),
                        chatChannelTitle = party_chat_channel.title,
                        userKeyId = user.key.id(),
                        userTitle = user.title,
                        userFirebaseUser = user.firebaseUser,
                        post_count = 0,
                        chatChannelRefKeyId = team.key.id(),
                        channel_type = 'team',
                        #chatChannelOwnerKeyId = user.key.id()
                    )

                    chat_message = "> Joined party chat"

                    ## push the chat channel list and a chat message

                    taskUrl='/task/chat/channel/list_changed'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                    'userKeyId': user.key.id(),
                                                                                    'textMessage': chat_message
                                                                                    }, countdown = 2)

                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': user.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })

                    ## queue up the task to send a message to all team members
                    taskUrl='/task/team/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)



                return self.render_json_response(
                    authorization = True,
                    player_authorized = authorized,
                    player_previously_active = previously_active,
                    user_key_id = str(user_key_id),
                    player_name = player_name,
                    player_currency = player_currency,
                    player_rank = player_rank,
                    player_userid = player_userid,
                    game_player_key_id = str(game_player_key_id)
                )



            else:
                logging.info('No access_token found - doing it the old way - deprecated')

                game = GamesController().get_by_key_id(server.gameKeyId)

                if game:
                    ##  just send a disvord error
                    if game.discord_subscribe_errors and game.discord_webhook_admin:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "Player activate request failed.  No Access Token was supplied.  Please update the UETOPIA plugin and game code to the latest version."
                        url = "http://ue4topia.appspot.com/"
                        discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)

            return self.render_json_response(
                authorization = True,
                player_authorized = authorized,
                player_previously_active = previously_active,
                user_key_id = str(user_key_id),
                player_name = player_name,
                player_currency = player_currency,
                player_rank = player_rank,
                player_userid = player_userid,
                game_player_key_id = str(game_player_key_id)
            )
