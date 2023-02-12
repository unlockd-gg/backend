import logging
import datetime
import string
import json
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.providers.compute_engine_zonemap import region_zone_mapper
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController
from configuration import *

class matchBeginHandler(BaseHandler):
    def post(self):
        """
        Begin a match
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, attackingPlayerKeyId, defendingPlayerKeyId, gameModeKeyId, region, metaMatchKeyId
        """

        serverController = ServersController()
        ucontroller = UsersController()
        gpController = GamePlayersController()
        gameController = GamesController()
        #gameCharacterController = GameCharactersController()
        teamMembersController = TeamMembersController()
        #gamePlayerSnapshotController = GamePlayerSnapshotController()
        gamePlayerController = GamePlayersController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGameController = GroupGamesController()
        matchController = MatchController()
        gameModeController = GameModesController()
        matchPlayerController = MatchPlayersController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        try:
            game = gameController.verify_signed_auth(self.request)
        except:
            game = False

        if game == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                request_successful = False
            )
        else:
            logging.info('auth success')

        logging.info(self.request)

        # get the game mode
        game_mode = gameModeController.get_by_gameKeyId_onlineSubsystemReference(game.key.id(), 'metagame')
        if not game_mode:
            logging.info('did not find game_mode')
            return self.render_json_response(
                authorization = True,
                error= "The game mode was not found.",
                request_successful = False
                )

        # get the attacking game player
        attacking_game_player = gamePlayerController.get_by_key_id(int(self.request.get('attackingPlayerKeyId')))
        if not attacking_game_player:
            logging.info('did not find attacking_game_player')
            return self.render_json_response(
                authorization = True,
                error= "The attacking game player was not found.",
                request_successful = False
                )

        # get the attacking team captain
        ## this might - or might not exist...
        attacking_team_member_captain = teamMembersController.get_by_gameKeyId_userKeyId(game.key.id(), int(attacking_game_player.userKeyId))
        if not attacking_team_member_captain:
            logging.info('did not find attacking_team_member_captain')
            return self.render_json_response(
                authorization = True,
                error= "The attacking game player team record was not found.",
                request_successful = False
                )

        # get the attacking team members (do we need the team itself?)
        attacking_team_members = teamMembersController.get_by_teamKeyId(attacking_team_member_captain.teamKeyId)
        ## TODO - any checks on this?

        #get the defending game player
        defending_game_player = gamePlayerController.get_by_key_id(int(self.request.get('defendingPlayerKeyId')))
        if not defending_game_player:
            logging.info('did not find defending_game_player')
            return self.render_json_response(
                authorization = True,
                error= "The defending game player was not found.",
                request_successful = False
                )

        # get the defending team captain
        ## this might - or might not exist...
        defending_team_member_captain = teamMembersController.get_by_gameKeyId_userKeyId(game.key.id(), defending_game_player.userKeyId)
        if not defending_team_member_captain:
            logging.info('did not find defending_team_member_captain')
            return self.render_json_response(
                authorization = True,
                error= "The defending game player team record was not found.",
                request_successful = False
                )

        # get the defending team members (do we need the team itself?)
        defending_team_members = teamMembersController.get_by_teamKeyId(defending_team_member_captain.teamKeyId)
        ## TODO - any checks on this?



        # create the match record

        match = matchController.create(
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            playersPerTeam = game_mode.playersPerTeam,
            teams = game_mode.teams,

            apiKey = matchController.create_unique_api_key(),
            apiSecret = matchController.key_generator(),
            title = "metagame",
            admissionFee = 0,
            gameModeKeyId = game_mode.key.id(),
            gameModeTitle = game_mode.onlineSubsystemReference,
            ## TODO add match initialization settings

            continuous_server_region = self.request.get('region'),
            continuous_server_zone = region_zone_mapper(self.request.get('region')),
            continuous_server_machine_type = game.match_deploy_vm_machine_type,
            admissionFeePerPlayer = game_mode.admissionFeePerPlayer,
            winRewardPerPlayer = game_mode.winRewardPerPlayer,
            metaMatchKeyId = int(self.request.get('metaMatchKeyId')),
            metaMatchTravelUrl = self.request.get('metaMatchTravelUrl'),
            metaMatchCustom = self.request.get('metaMatchCustom')
        )

        # create the chat channels
        match_chat_title = "match chat"
        match_chat_channel = chatChannelController.create(
            title = match_chat_title,
            channel_type = 'match',
            #adminUserKeyId = authorized_user.key.id(),
            refKeyId = match.key.id(),
            gameKeyId = game.key.id(),
            max_subscribers = 200
        )

        ## set up the team chat channel
        if game_mode.playersPerTeam > 1:
            attacker_chat_title = match.title + "attacker team chat"
            attacker_chat_channel = chatChannelController.create(
                title = attacker_chat_title,
                channel_type = 'matchteam',
                gameKeyId = game.key.id(),
                max_subscribers = 200
            )
            attacker_chat_channel_key_id = attacker_chat_channel.key.id()

            defender_chat_title = match.title + "defender team chat"
            defender_chat_channel = chatChannelController.create(
                title = defender_chat_title,
                channel_type = 'matchteam',
                gameKeyId = game.key.id(),
                max_subscribers = 200
            )
            defender_chat_channel_key_id = defender_chat_channel.key.id()


        # assign the match players - which should  already exist
        ## get attacking team match players
        for attacking_team_member in attacking_team_members:
            attacking_match_player = matchPlayerController.get_pending_by_gameKeyId_userKeyId(game.key.id(), attacking_team_member.userKeyId)
            if not attacking_match_player:
                logging.info('attacking match player not found - this can happen if a user finishes a match, and just waits at the lobby without starting matchmaker again')
                ## This is OK, as the metagame server will get notified on logout.
                ## TODO notify the metagame server if a user starts matchmaking in a different mode.  eg. played metamode, then clicks 1v1

            else:
                logging.info('found attacking match player')

                attacking_match_player.matchmakerPending = False
                attacking_match_player.matchmakerFoundMatch = True
                attacking_match_player.teamId = 0
                attacking_match_player.matchKeyId = match.key.id()
                attacking_match_player.session_host_address = match.hostConnectionLink
                attacking_match_player.session_id = match.session_id

                # save
                matchPlayerController.update(attacking_match_player)

                # subscribe the player to the chat channel(s)
                subscriber = chatChannelSubscribersController.create(
                    online = True,
                    chatChannelKeyId = match_chat_channel.key.id(),
                    chatChannelTitle = match_chat_channel.title,
                    userKeyId = attacking_match_player.userKeyId,
                    userTitle = attacking_match_player.userTitle,
                    userFirebaseUser = attacking_match_player.firebaseUser,
                    post_count = 0,
                    chatChannelRefKeyId = match.key.id(),
                    channel_type = 'match',
                    #chatChannelOwnerKeyId = authorized_user.key.id()
                )

                chat_message = "> Joined match chat"

                ## subscribe them to the team chat
                if game_mode.playersPerTeam > 1:
                    chat_message = chat_message + " and match team chat"

                    subscriber = chatChannelSubscribersController.create(
                        online = True,
                        chatChannelKeyId = attacker_chat_channel.key.id(),
                        chatChannelTitle = attacker_chat_channel.title,
                        userKeyId = attacking_match_player.userKeyId,
                        userTitle = attacking_match_player.userTitle,
                        userFirebaseUser = attacking_match_player.firebaseUser,
                        post_count = 0,
                        chatChannelRefKeyId = attacking_match_player.teamKeyId,
                        channel_type = 'matchteam',
                        #chatChannelOwnerKeyId = authorized_user.key.id()
                    )

                taskUrl='/task/chat/channel/list_changed'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': attacking_match_player.firebaseUser,
                                                                                'userKeyId': attacking_match_player.userKeyId,
                                                                                'textMessage': chat_message
                                                                                }, countdown = 2)

                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': attacking_match_player.firebaseUser,
                                                                                    "message": chat_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })


        ## get defending team match players
        for defending_team_member in defending_team_members:
            defending_match_player = matchPlayerController.get_pending_by_gameKeyId_userKeyId(game.key.id(), defending_team_member.userKeyId)
            if not defending_match_player:
                logging.info('defending match player not found - this should not happen')
                ## TODO -deal with this.  It's probably safe to just make a new one?
            else:
                logging.info('found defending match player')

                defending_match_player.matchmakerPending = False
                defending_match_player.matchmakerFoundMatch = True
                defending_match_player.teamId = 1
                defending_match_player.matchKeyId = match.key.id()
                defending_match_player.session_host_address = match.hostConnectionLink
                defending_match_player.session_id = match.session_id

                # save
                matchPlayerController.update(defending_match_player)

                # subscribe the player to the chat channel(s)
                subscriber = chatChannelSubscribersController.create(
                    online = True,
                    chatChannelKeyId = match_chat_channel.key.id(),
                    chatChannelTitle = match_chat_channel.title,
                    userKeyId = defending_match_player.userKeyId,
                    userTitle = defending_match_player.userTitle,
                    userFirebaseUser = defending_match_player.firebaseUser,
                    post_count = 0,
                    chatChannelRefKeyId = match.key.id(),
                    channel_type = 'match',
                    #chatChannelOwnerKeyId = authorized_user.key.id()
                )

                chat_message = "> Joined match chat"

                ## subscribe them to the team chat
                if game_mode.playersPerTeam > 1:
                    chat_message = chat_message + " and match team chat"

                    subscriber = chatChannelSubscribersController.create(
                        online = True,
                        chatChannelKeyId = defender_chat_channel.key.id(),
                        chatChannelTitle = defender_chat_channel.title,
                        userKeyId = defending_match_player.userKeyId,
                        userTitle = defending_match_player.userTitle,
                        userFirebaseUser = defending_match_player.firebaseUser,
                        post_count = 0,
                        chatChannelRefKeyId = defending_match_player.teamKeyId,
                        channel_type = 'matchteam',
                        #chatChannelOwnerKeyId = authorized_user.key.id()
                    )

                taskUrl='/task/chat/channel/list_changed'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': defending_match_player.firebaseUser,
                                                                                'userKeyId': defending_match_player.userKeyId,
                                                                                'textMessage': chat_message
                                                                                }, countdown = 2)

                taskUrl='/task/chat/send'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': defending_match_player.firebaseUser,
                                                                                    "message": chat_message,
                                                                                    "created":datetime.datetime.now().isoformat()
                                                                                })




        #
        ## add the message to the database
        chat_message_copy = "Metagame Match starting.  Bringing up a server."
        chat_message = chat_message_controller.create(
            chatChannelKeyId = match_chat_channel.key.id(),
            chatChannelTitle = match_chat_channel.title,
            #userKeyId = authorized_user.key.id(),
            #userTitle = authorized_user.title,
            text = chat_message_copy,
            #pulled = False
        )

        taskUrl='/task/chat/channel/send'
        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': match_chat_channel.key.id(),
                                                                            "message": chat_message_copy,
                                                                            #"userKeyId": authorized_user.key.id(),
                                                                            #"userTitle": authorized_user.title,
                                                                            "chatMessageKeyId": chat_message.key.id(),
                                                                            "chatChannelTitle": match_chat_channel.title,
                                                                            "chatChannelRefType":match_chat_channel.channel_type,
                                                                            "created":chat_message.created.isoformat()
                                                                        }, countdown = 2)

        ## start a task to create the vm
        ## TODO - first check to see if localtesting is enabled.
        taskUrl='/task/matchmaker/vm/allocate'
        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                "matchKeyId": match.key.id()
                                                                            })


        return self.render_json_response(
            authorization = True,
            request_successful=True
        )
