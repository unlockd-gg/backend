import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController
from configuration import *

class DeactivateStaleMatchPlayersHandler(BaseHandler):
    def get(self):
        logging.info('Cron Deactivate Stale Players')

        mpController = MatchPlayersController()
        matchController = MatchController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chatMessageController = ChatMessagesController()

        expired_players = mpController.list_pending_stale()

        description = "Detected a stale pending match, and deleted it."

        for player in expired_players:

            player.matchmakerFoundMatch = False
            player.matchmakerJoinable = False
            player.matchmakerJoinPending = False
            player.matchmakerPending = False
            player.matchmakerServerReady = False
            player.stale_requires_check = False
            player.stale = None

            mpController.update(player)

            processed_matchKeyIds = []

            ## push an alert out to firebase
            taskUrl='/task/user/alert/create'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': player.firebaseUser,
                                                                            'material_icon': MATERIAL_ICON_MATCH_PLAYER_EXPIRED,
                                                                            'importance': 'md-primary',
                                                                            ## TODO this message can be more helpful
                                                                            'message_text': description,
                                                                            #'action_button_color': 'primary',
                                                                            #'action_button_sref': '#/user/transactions'
                                                                            }, countdown = 1,)

            ## Deal with the match too!
            #also get the match and remove it
            ## if it's part of a tournament - uhhh do something


            if player.matchKeyId:
                logging.info('found a match associated with this player')
                if not player.matchKeyId in processed_matchKeyIds:
                    logging.info('the match has not been processed yet')
                    match = matchController.get_by_key_id(player.matchKeyId)
                    if match:
                        processed_matchKeyIds.append(player.matchKeyId)
                        if match.tournamentKeyId:
                            logging.info('this match is part of a tournament')
                            ## TODO deal with this.
                        else:
                            logging.info('this match is not part of a tournament')
                            match.matchExpired = True
                            match.match_active = False
                            match.matchVerified = False
                            match.match_provisioned = False
                            match.match_destroying = True
                            match.match_destroying_timestamp = datetime.datetime.now()
                            ## also clear out api key/secret
                            match.apiKey = None
                            match.apiSecret = None

                            ## In match results the following flags are set
                            """
                            match.matchVerified = True
                            match.allPlayersVerified = True

                            match.match_active = False
                            match.match_provisioned = False
                            match.match_creating = False
                            #match.continuous_server_creating_timestamp = None
                            match.match_destroying = True
                            match.match_destroying_timestamp = datetime.datetime.now()
                            match.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
                            match.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
                            match.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value
                            """

                            matchController.update(match)

                            ## FINALIZE IT SO IT DOES NOT KEEP GETTING PICKED UP

                            ## TODO also fire off a VM check here, just in case

                            ## also delete the chat channels and subscribers
                            ## don't bother sending out messages - just clear it.

                            match_chat_channel = chatChannelController.get_by_channel_type_refKeyId("match", match.key.id())
                            if match_chat_channel:
                                logging.info('found match_chat_channel')
                                if not match_chat_channel in match_chat_channels_to_delete:
                                    logging.info('adding match_chat_channel to array for deletion')
                                    match_chat_channels_to_delete.append(match_chat_channel)

                                match_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_chat_channel.key.id(), player.userKeyId )
                                if match_chat_channel_subscriber:
                                    logging.info('found match_chat_channel_subscriber - deleting')
                                    chatChannelSubscribersController.delete(match_chat_channel_subscriber)

                            ## get the team chat channel
                            if player.teamKeyId:  ## this is a match player!
                                logging.info('found teamKeyId')
                                match_team_chat_channel = chatChannelController.get_by_channel_type_refKeyId("matchteam", player.teamKeyId)
                                if match_team_chat_channel:
                                    logging.info('found match_team_chat_channel')

                                    if not match_team_chat_channel in match_team_chat_channels_to_delete:
                                        logging.info('adding match_team_chat_channel to array for deletion')
                                        match_team_chat_channels_to_delete.append(match_team_chat_channel)

                                    match_team_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_team_chat_channel.key.id(), player.userKeyId )
                                    if match_team_chat_channel_subscriber:
                                        logging.info('found match_team_chat_channel_subscriber - deleting')
                                        chatChannelSubscribersController.delete(match_team_chat_channel_subscriber)

                            ## check to see if this game is in local testing mode
                            if match.continuous_server_project != 'localtesting':
                                logging.info('not a local match')

                                ## start a task to dealoocate the VM
                                taskUrl='/task/matchmaker/vm/deallocate'
                                vmTitle = "m%s" %match.key.id()
                                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': 'ue4topia',
                                                                                                        "zone": match.continuous_server_zone,
                                                                                                        "name": vmTitle,
                                                                                                        "matchKeyId": match.key.id()
                                                                                                    }, countdown=MATCHMAKER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS)



        playercount = len(expired_players)

        expired_joinable = mpController.list_joinable_stale()

        description = "Detected a stale joinable match, and deleted it."


        ## keep track of chat channels to delete - we need them until the end
        ## TODO - this could be optimized to reduce the lookups
        match_chat_channels_to_delete = []
        match_team_chat_channels_to_delete = []

        for player in expired_joinable:


            #also get the match and remove it
            ## if it's part of a tournament - uhhh do something
            if player.matchKeyId:
                logging.info('found a match associated with this player')
                if not player.matchKeyId in processed_matchKeyIds:
                    logging.info('the match has not been processed yet')
                    match = matchController.get_by_key_id(player.matchKeyId)
                    if match:
                        processed_matchKeyIds.append(player.matchKeyId)
                        if match.tournamentKeyId:
                            logging.info('this match is part of a tournament')
                            ## TODO deal with this.
                        else:
                            logging.info('this match is not part of a tournament')
                            match.matchExpired = True
                            match.match_active = False
                            match.matchVerified = False
                            match.match_provisioned = False
                            match.match_destroying = True
                            match.match_destroying_timestamp = datetime.datetime.now()
                            ## also clear out api key/secret
                            match.apiKey = None
                            match.apiSecret = None

                            ## In match results the following flags are set
                            """
                            match.matchVerified = True
                            match.allPlayersVerified = True

                            match.match_active = False
                            match.match_provisioned = False
                            match.match_creating = False
                            #match.continuous_server_creating_timestamp = None
                            match.match_destroying = True
                            match.match_destroying_timestamp = datetime.datetime.now()
                            match.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
                            match.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
                            match.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value
                            """

                            matchController.update(match)

                            ## FINALIZE IT SO IT DOES NOT KEEP GETTING PICKED UP

                            ## TODO also fire off a VM check here, just in case

                            ## also delete the chat channels and subscribers
                            ## don't bother sending out messages - just clear it.

                            match_chat_channel = chatChannelController.get_by_channel_type_refKeyId("match", match.key.id())
                            if match_chat_channel:
                                logging.info('found match_chat_channel')
                                if not match_chat_channel in match_chat_channels_to_delete:
                                    logging.info('adding match_chat_channel to array for deletion')
                                    match_chat_channels_to_delete.append(match_chat_channel)

                                match_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_chat_channel.key.id(), player.userKeyId )
                                if match_chat_channel_subscriber:
                                    logging.info('found match_chat_channel_subscriber - deleting')
                                    chatChannelSubscribersController.delete(match_chat_channel_subscriber)

                            ## get the team chat channel
                            if player.teamKeyId:  ## this is a match player!
                                logging.info('found teamKeyId')
                                match_team_chat_channel = chatChannelController.get_by_channel_type_refKeyId("matchteam", player.teamKeyId)
                                if match_team_chat_channel:
                                    logging.info('found match_team_chat_channel')

                                    if not match_team_chat_channel in match_team_chat_channels_to_delete:
                                        logging.info('adding match_team_chat_channel to array for deletion')
                                        match_team_chat_channels_to_delete.append(match_team_chat_channel)

                                    match_team_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_team_chat_channel.key.id(), player.userKeyId )
                                    if match_team_chat_channel_subscriber:
                                        logging.info('found match_team_chat_channel_subscriber - deleting')
                                        chatChannelSubscribersController.delete(match_team_chat_channel_subscriber)



            player.matchmakerFoundMatch = False
            player.matchmakerJoinable = False
            player.matchmakerJoinPending = False
            player.matchmakerPending = False
            player.matchmakerServerReady = False
            player.stale_requires_check = False
            player.stale = None

            mpController.update(player)

            ## push an alert out to firebase
            taskUrl='/task/user/alert/create'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': player.firebaseUser,
                                                                            'material_icon': MATERIAL_ICON_MATCH_PLAYER_EXPIRED,
                                                                            'importance': 'md-primary',
                                                                            ## TODO this message can be more helpful
                                                                            'message_text': description,
                                                                            #'action_button_color': 'primary',
                                                                            #'action_button_sref': '#/user/transactions'
                                                                            }, countdown = 1,)

        playercount = playercount + len(expired_joinable)


        ## joinPending - this occurs if the server never even starts - devs see this a lot before they get server running

        expired_joinable = mpController.list_joinPending_stale()

        description = "Detected a stale join pending match, and deleted it."


        for player in expired_joinable:


            #also get the match and remove it
            ## if it's part of a tournament - uhhh do something
            if player.matchKeyId:
                logging.info('found a match associated with this player')
                if not player.matchKeyId in processed_matchKeyIds:
                    logging.info('the match has not been processed yet')
                    match = matchController.get_by_key_id(player.matchKeyId)
                    if match:
                        logging.info('got the match')
                        processed_matchKeyIds.append(player.matchKeyId)
                        if match.tournamentKeyId:
                            logging.info('this match is part of a tournament')
                            ## TODO deal with this.
                        else:
                            logging.info('this match is not part of a tournament')
                            match.matchExpired = True
                            match.match_active = False
                            match.matchVerified = False
                            match.match_provisioned = False
                            match.match_destroying = True
                            match.match_destroying_timestamp = datetime.datetime.now()
                            ## also clear out api key/secret
                            match.apiKey = None
                            match.apiSecret = None
                            matchController.update(match)

                            ## also delete the chat channels and subscribers
                            ## don't bother sending out messages - just clear it.

                            match_chat_channel = chatChannelController.get_by_channel_type_refKeyId("match", match.key.id())
                            if match_chat_channel:
                                logging.info('found match_chat_channel')
                                if not match_chat_channel in match_chat_channels_to_delete:
                                    logging.info('adding match_chat_channel to array for deletion')
                                    match_chat_channels_to_delete.append(match_chat_channel)

                                match_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_chat_channel.key.id(), player.userKeyId )
                                if match_chat_channel_subscriber:
                                    logging.info('found match_chat_channel_subscriber - deleting')
                                    chatChannelSubscribersController.delete(match_chat_channel_subscriber)

                            ## get the team chat channel
                            if player.teamKeyId:  ## this is a match player!
                                logging.info('found teamKeyId')
                                match_team_chat_channel = chatChannelController.get_by_channel_type_refKeyId("matchteam", player.teamKeyId)
                                if match_team_chat_channel:
                                    logging.info('found match_team_chat_channel')

                                    if not match_team_chat_channel in match_team_chat_channels_to_delete:
                                        logging.info('adding match_team_chat_channel to array for deletion')
                                        match_team_chat_channels_to_delete.append(match_team_chat_channel)

                                    match_team_chat_channel_subscriber = chatChannelSubscribersController.get_by_channel_and_user(match_team_chat_channel.key.id(), player.userKeyId )
                                    if match_team_chat_channel_subscriber:
                                        logging.info('found match_team_chat_channel_subscriber - deleting')
                                        chatChannelSubscribersController.delete(match_team_chat_channel_subscriber)



            player.matchmakerFoundMatch = False
            player.matchmakerJoinable = False
            player.matchmakerJoinPending = False
            player.matchmakerPending = False
            player.matchmakerServerReady = False
            player.stale_requires_check = False
            player.stale = None

            mpController.update(player)

            ## push an alert out to firebase
            taskUrl='/task/user/alert/create'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': player.firebaseUser,
                                                                            'material_icon': MATERIAL_ICON_MATCH_PLAYER_EXPIRED,
                                                                            'importance': 'md-primary',
                                                                            ## TODO this message can be more helpful
                                                                            'message_text': description,
                                                                            #'action_button_color': 'primary',
                                                                            #'action_button_sref': '#/user/transactions'
                                                                            }, countdown = 1,)

        playercount = playercount + len(expired_joinable)

        ## now go through the chat channels we have collected, and delete those too
        for match_chat_channel_to_delete in match_chat_channels_to_delete:
            logging.info('deleting match chat channel')
            chatChannelController.delete(match_chat_channel_to_delete)

        for match_team_chat_channel_to_delete in match_team_chat_channels_to_delete:
            logging.info('deleting match team chat channel')
            chatChannelController.delete(match_team_chat_channel_to_delete)

        return self.render_json_response(
            playercount = playercount
        )
