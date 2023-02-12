import logging
import datetime
import json
import random
import uuid
from google.appengine.api import taskqueue
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *


spController = ServerPlayersController()
serverController = ServersController()
gamePlayerController = GamePlayersController()
lockController = TransactionLockController()
transactionController = TransactionsController()
chatChannelSubscribersController = ChatChannelSubscribersController()
chatChannelController = ChatChannelsController()
gameController = GamesController()

def deactivate_player2(server_player, new_rank, transfer=False, user=None):
    """ New version - for server hold elimination """
    if server_player.pending_authorize:
        logging.info('server_player Set to pending authorize')

    if server_player.active:
        logging.info('server_player Set to active')
        previously_active = True

    if server_player.pending_deauthorize:
        logging.info('server_player Set to pending deauthorize')

    #player_btchold = server_player.currencyCurrent

    player_rank = server_player.ladderRank

    ## Update the server player member record
    server_player.active = False
    server_player.admission_paid = False
    #server_player.authorized = True

    if new_rank:
        server_player.ladderRank = int(new_rank)

    #if satoshi_balance:
    #    server_player.btcHoldEnd = int(satoshi_balance)

    if transfer:
        #server_player.currencyCurrent = 0
        server_player.active = False
        server_player.authorized = False

    chat_message = ""
    if user:
        logging.info('deactivate_player2: Found User')
        ## we have a user so we can send a custom chat message
        ## we need the game, and game player to do this.
        ## First setup the message with the guild tag if set
        if user.groupTag:
            chat_message = "%s " % user.groupTag

        game = gameController.get_by_key_id(server_player.gameKeyId)
        if game:
            logging.info('deactivate_player2: Found Game')

            if game.characters_enabled:
                logging.info('deactivate_player2: characters enabled')

                game_player = gamePlayerController.get_by_gameKeyId_userKeyId(server_player.gameKeyId, user.key.id())
                if game_player:
                    logging.info('deactivate_player2: found existing game player')

                    chat_message = chat_message + "%s left" % game_player.characterCurrentTitle
                else:
                    chat_message = chat_message + "%s left" % user.title
            else:
                chat_message = chat_message + "%s left" % user.title
        else:
            chat_message = chat_message + "%s left" % user.title




    active_server_players = spController.get_list_active_by_server(server_player.serverKeyId)

    logging.info('active_server_players: %s'%len(active_server_players))

    ## Grab the game and server so we can populate server data into the feed
    server = serverController.get_by_key_id(server_player.serverKeyId)
    game = GamesController().get_by_key_id(server_player.gameKeyId)

    if len(active_server_players) <= 1:
        logging.info('last player to deactivate. ')

        ## check for a dynamic server - deallocate it.
        if server:
            if server.continuous_server:
                logging.info("continuous_server")

                delaytime = random.randint(1,CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_RANDOMIZE_SECONDS) + CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS
                logging.info('countdown delay: %s' %delaytime)


                ## start a task to check on the server after our timer
                taskUrl='/task/server/vm/checkunused'
                taskqueue.add(url=taskUrl, queue_name='serverCheckUnused', params={"serverKeyId": server.key.id()
                                                                                    }, countdown=delaytime)




    else:
        logging.info("there are still active players")


    spController.update(server_player)

    ## update firebase friends

    taskUrl='/task/user/firebase/update'
    ##playingLink = '/#/game/%s'%(game.key.id())
    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.userKeyId, 'online': False }, countdown = 2,)

    ##  update firebase server player record
    #taskUrl='/task/server/player/firebase/update'
    #taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id()}, countdown = 2,)
    taskUrl='/task/server/player/firebase/update'
    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id(), 'connecting': 'false', 'disconnecting': 'true'}, countdown = 2,)

    taskUrl='/task/server/firebase/update'
    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server.key.id()}, countdown = 2,)

    ## unsubscribe the player from the chat channel
    server_chat_channel = chatChannelController.get_by_channel_type_refKeyId('server', server.key.id())
    if server_chat_channel:
        existing_chat_subscriber = chatChannelSubscribersController.get_by_channel_and_user(server_chat_channel.key.id(), server_player.userKeyId)
        if existing_chat_subscriber:
            chatChannelSubscribersController.delete(existing_chat_subscriber)
            # push chat channels and a chat message
            #chat_message = "%s left" % server_player.userTitle

            taskUrl='/task/chat/channel/list_changed'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': server_player.firebaseUser,
                                                                            'userKeyId': server_player.userKeyId,
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

        #taskUrl='/task/chat/send'
        #taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': server_player.firebaseUser,
        #                                                                    "message": chat_message,
        #                                                                    "created":datetime.datetime.now().isoformat()
        #                                                                })

def deactivate_player(server_player, new_rank, satoshi_balance, transfer=False):
    if server_player.pending_authorize:
        logging.info('server_player Set to pending authorize')

    if server_player.active:
        logging.info('server_player Set to active')
        previously_active = True

    if server_player.pending_deauthorize:
        logging.info('server_player Set to pending deauthorize')

    player_btchold = server_player.currencyCurrent

    player_rank = server_player.ladderRank

    ## Update the server player member record
    server_player.active = False
    server_player.admission_paid = False
    #server_player.authorized = True

    if new_rank:
        server_player.ladderRank = int(new_rank)

    if satoshi_balance:
        server_player.btcHoldEnd = int(satoshi_balance)

    if transfer:
        #server_player.currencyCurrent = 0
        server_player.active = False
        server_player.authorized = False


    active_server_players = spController.get_list_active_by_server(server_player.serverKeyId)

    logging.info('active_server_players: %s'%len(active_server_players))

    ## Grab the game and server so we can populate server data into the feed
    server = serverController.get_by_key_id(server_player.serverKeyId)
    game = GamesController().get_by_key_id(server_player.gameKeyId)

    # if we have setup auto-auth, we shoud refund the player's currency here.
    # we need the game player for this.
    gamePlayer = gamePlayerController.get_by_gameKeyId_userKeyId(server_player.gameKeyId, server_player.userKeyId)

    if gamePlayer:
        logging.info('gamePlayer found')
        if gamePlayer.autoAuth:
            logging.info('autoAuth is ON')
            # only do it if it's a positive amount
            if server_player.currencyCurrent > 0:
                ## One for the player

                ## if it's a transfer, there is no transaction....  It is sent over to the new serverplayer instead.
                ## this isn't working.  disabling currency transfer.  all servers auth and deauth independantly
                """
                if transfer:
                    ## send an alert, so the user knows what's up.
                    description = "%s CRED transferred to %s" %(server.admissionFee, server.title)
                    taskUrl='/task/user/alert/create'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': gamePlayer.firebaseUser,
                                                                                    'material_icon': MATERIAL_ICON_TRANSFER,
                                                                                    'importance': 'md-primary',
                                                                                    ## TODO this message can be more helpful
                                                                                    'message_text': description,
                                                                                    'action_button_color': 'primary',
                                                                                    'action_button_sref': '/profile'
                                                                                    }, countdown = 0,)
                else:
                """
                description = "Left server: %s" %server.title
                transactionController.create(
                    amountInt = server_player.currencyCurrent,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    userKeyId = gamePlayer.userKeyId,
                    firebaseUser = gamePlayer.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    ##serverKeyId = server.key.id(),
                    ##serverTitle = server.title()
                    ##  transactions are batched and processed all at once.
                    transactionType = "user",
                    transactionClass = "deauthorize",
                    transactionSender = False,
                    transactionRecipient = True,
                    ##recipientTransactionKeyId = recipient_transaction.key.id(),
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_SERVER_DEAUTHORIZE,
                    materialDisplayClass = "md-primary"
                )

                ## Create a transaction for the serverplayer
                ## this is going to be applied directly, and will be marked as processed.

                description = "Left server"

                ## Create a transaction for the withdrawl -user
                transactionServerPlayer = TransactionsController().create(
                    userKeyId = gamePlayer.userKeyId,
                    firebaseUser = gamePlayer.firebaseUser,
                    description = description,
                    amountInt = -server_player.currencyCurrent,
                    newBalanceInt = 0,
                    serverPlayerKeyId = server_player.key.id(),
                    transactionType = "serverplayer",
                    transactionClass = "server deactivate",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = True,
                    materialIcon = MATERIAL_ICON_SERVER_AUTHORIZE,
                    materialDisplayClass = "md-accent"
                    )


                ## zero out balance
                server_player.currencyCurrent = 0


    pushable = lockController.pushable("user:%s"%gamePlayer.userKeyId)
    if pushable:
        logging.info('user pushable')
        taskUrl='/task/user/transaction/process'
        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                            "key_id": gamePlayer.userKeyId
                                                                        }, countdown=2)


    #latest_status = gdsController.get_latest_by_serverKey(server_player.serverKey)

    if len(active_server_players) <= 1:
        logging.info('last player to deactivate. ')


        ## check for a dynamic server - deallocate it.
        if server.continuous_server:
            logging.info("continuous_server")

            delaytime = random.randint(1,CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_RANDOMIZE_SECONDS) + CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS
            logging.info('countdown delay: %s' %delaytime)


            ## start a task to check on the server after our timer
            taskUrl='/task/server/vm/checkunused'
            taskqueue.add(url=taskUrl, queue_name='serverCheckUnused', params={"serverKeyId": server.key.id()
                                                                                }, countdown=delaytime)




    else:
        logging.info("there are still active players")


    spController.update(server_player)

    ## update firebase friends

    taskUrl='/task/user/firebase/update'
    ##playingLink = '/#/game/%s'%(game.key.id())
    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.userKeyId, 'online': True }, countdown = 2,)

    ##  update firebase server player record
    #taskUrl='/task/server/player/firebase/update'
    #taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id()}, countdown = 2,)
    taskUrl='/task/server/player/firebase/update'
    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': server_player.key.id(), 'connecting': 'false', 'disconnecting': 'true'}, countdown = 2,)

    ## unsubscribe the player from the chat channel
    server_chat_channel = chatChannelController.get_by_channel_type_refKeyId('server', server.key.id())
    if server_chat_channel:
        existing_chat_subscriber = chatChannelSubscribersController.get_by_channel_and_user(server_chat_channel.key.id(), server_player.userKeyId)
        if existing_chat_subscriber:
            chatChannelSubscribersController.delete(existing_chat_subscriber)
            # push chat channels and a chat message
            chat_message = "%s left" % server_player.userTitle

            taskUrl='/task/chat/channel/list_changed'
            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': server_player.firebaseUser,
                                                                            'userKeyId': server_player.userKeyId,
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

        #taskUrl='/task/chat/send'
        #taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': server_player.firebaseUser,
        #                                                                    "message": chat_message,
        #                                                                    "created":datetime.datetime.now().isoformat()
        #                                                                })
