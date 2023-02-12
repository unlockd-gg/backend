import logging
import datetime
import string
import json
import time
import hashlib
import hmac
import urllib
import httplib
from collections import OrderedDict
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from httplib2 import Http
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.match_task_status import MatchTaskStatusController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController
from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.ads import AdsController
from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.server_shard_placeholder import ServerShardPlaceholderController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class MatchmakerStartHandler(BaseHandler):
    def post(self, gameKeyId):
        """
        Start Matchmaking for a game
        Requires http headers:  -
        Requires POST parameters:  - userid, matchtype
        """

        ## check this userid
        ## get the game player
        ## are there any existing matches

        ## Run auth.  we have our JWT
        userController = UsersController()

        try:
            id_token = self.request.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')

        if id_token:
            logging.info("id_token: %s" %id_token)

            # Verify Firebase auth.
            #logging.info(self.request_state)

            claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
            if not claims:
                logging.error('Firebase Unauth')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                )

            user = userController.get_by_firebaseUser(claims['user_id'])

            if not user:
                logging.info('no user record found')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                )
        else:
            return self.render_json_response(
                authorization = True,
                success = False,
            )

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        #if 'userid' in jsonobject:
        #    logging.info("Found userid in json")
        #    userid = int(jsonobject['userid'])
        #else:
        #    return self.render_json_response(
        #        authorization = True,
        #        success = False,
        #        response_message = "userid is required"
        #    )

        if 'matchtype' in jsonobject:
            logging.info("Found matchtype in json")
            matchtype = jsonobject['matchtype']
        else:
            logging.info('matchtype not found.  Defaulting to 1v1')
            matchtype = '1v1'

        logging.info("matchtype: %s" %matchtype)

        gameController = GamesController()
        gpController = GamePlayersController()
        mtsController = MatchTaskStatusController()
        mpController = MatchPlayersController()
        gmController = GameModesController()
        adController = AdsController()

        tournamentController = TournamentsController()
        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        gameCharacterController = GameCharactersController()

        groupController = GroupsController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGameController = GroupGamesController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        serverShardPlaceholderController = ServerShardPlaceholderController()

        ## Setup for pushes out to heroku
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        game = gameController.get_by_key_id(int(gameKeyId))
        if not game:
            logging.error('game was not found with the supplied key id')
            return self.render_json_response(
                authorization = True,
                response_successful = False,
                response_message = "game was not found"
            )

        userid = user.key.id()

        game_player = gpController.get_by_gameKeyId_userKeyId(int(gameKeyId), userid)

        if not game_player:
            logging.info('game player not found.')

            ## create the game player
            ## it's safe to just create it.

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
                # = 100000,
                autoTransfer = True,
                firebaseUser = user.firebaseUser,
                picture = user.picture,
                lastServerClusterKeyId = None,
                groupKeyId = user.groupTagKeyId,
                groupTag = user.groupTag,
                showGameOnProfile = True
            )



        ## make sure the game has a positive balance
        if game.currencyBalance < 0:
            logging.info('game balance is negative - cannot start matchmaking')

            if game.discord_subscribe_errors and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Error: Cannot start matchmaker when the game has a negative currency balance"
                url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)

            textMessage = "> Cannot start matchmaking.  The game's currency balance is negative.  You can donate to the game directly to fix this."

            chat_msg = json.dumps({"type":"chat",
                                    "textMessage":textMessage,
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

            return self.render_json_response(
                authorization = True,
                response_successful = False,
                response_message = "game balance was negative"
            )

        ## make sure we have a matching gameMode to work with
        game_mode = gmController.get_by_gameKeyId_onlineSubsystemReference(int(gameKeyId), matchtype)
        if not game_mode:
            logging.info('game mode not found.')

            if game.discord_subscribe_errors and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Error: %s attempted to start matchmaking, using %s game mode.  This game mode could not be found" % (user.title, matchtype)
                url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)

            return self.render_json_response(
                authorization = True,
                response_successful = False,
                response_message = "game mode was not found"
            )

        ## make sure the game mode has the required tags
        logging.info(game_mode.requireBadgeTags)
        if len(game_mode.requireBadgeTags) > 0:
            logging.info('found requireBadgeTags')
            player_has_all_tags = True
            missing_tags = []
            missingTagsTextMessage = "> You do not have the tags required to join this game mode.  You are missing: "
            for tag in game_mode.requireBadgeTags:
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

            if player_has_all_tags:
                logging.info('player has all required tags')
            else:
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

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = missingTagsTextMessage
                )



        ## calculate or create a stale timestamp from game max timeout
        ## this needs to be longer than the max timeout to ensure that the match is cancelled before the match player
        if game.match_timeout_max_minutes:
            timeout_duration_seconds = (game.match_timeout_max_minutes + 40) * 60
        else:
            timeout_duration_seconds = 100 * 60

        stale_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=timeout_duration_seconds)


        ## check to see if ads are required, and if so, are there any ads available
        if game_mode.ads_required:
            logging.info('ads are rquired to start matchmaking in this game mode')

            potential_ads = adController.get_active_highest_gameModeKeyId(game.key.id(), 1)

            if len(potential_ads) == 0:
                logging.info('There are no available ads - cannot start matchmaking')

                if game.discord_subscribe_errors and game.discord_webhook_admin:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Error: Matchmaker was requested to start on game mode: %s.  It is set to ADS REQUIRED.  But no ads are available." %game_mode.onlineSubsystemReference
                    url = "http://ue4topia.appspot.com/#/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)

                textMessage = "Error: Matchmaker was requested to start on game mode: %s.  It is set to ADS REQUIRED.  But no ads are available.  Consider sponsiring this game mode with your group." %game_mode.onlineSubsystemReference

                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
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
                    headers = {"Content-Type": "application/json"}
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

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "No Ads were available."
                )




        ## Check to see if this user is in a party/team
        ## run all checks for all members of the team

        current_user_team_member = teamMembersController.get_by_gameKeyId_userKeyId(int(gameKeyId), userid)
        if current_user_team_member:
            logging.info('found a team meber record')
            if not current_user_team_member.captain:
                logging.info('User is not captain - aborting')

                if game.discord_subscribe_errors and game.discord_webhook_admin:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Error: %s attempted to start matchmaking, but is not the team captain" % (user.title)
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "you are not the captain of your team."
                )

            ## We have the captain.

            ## Any other checks?
            ## get all of the team members
            all_team_members = teamMembersController.get_by_teamKeyId(current_user_team_member.teamKeyId)

            ## Check current team size against the game mode's minimum and maximum
            if game_mode.teamSizeMin:
                if len(all_team_members) < game_mode.teamSizeMin:
                    logging.info('team size is lower than game_mode.teamSizeMin')
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = "Not enough players in the party for this game mode."
                    )

            if game_mode.teamSizeMax:
                if len(all_team_members) > game_mode.teamSizeMax:
                    logging.info('team size is greater than game_mode.teamSizeMax')
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = "Too many players in the party for this game mode."
                    )



            ## keep track of the ranks, score and exp for the team
            team_rank_total = 0
            team_score_total = 0
            team_exp_total = 0

            for team_member in all_team_members:
                ## Get this user account
                team_member_user_record = userController.get_by_key_id(team_member.userKeyId)
                if not team_member_user_record:
                    logging.error('User not found from team member record')
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = "Internal error accessing a user's account"
                    )

                ## TODO - make sure this Team member has all of the required tags

                ## make sure the user has enough CRED to cover the admission fee set in gamemodes.
                if game_mode.admissionFeePerPlayer > team_member_user_record.currencyBalance:
                    logging.info('%s has insufficient balance' %team_member_user_record.title)

                    textMessage = "> Party member %s does not have sufficient balance to join this match" % user.title

                    chat_msg = json.dumps({"type":"chat",
                                            "textMessage":textMessage,
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
                        headers = {"Content-Type": "application/json"}
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

                    if game.discord_subscribe_errors and game.discord_webhook_admin:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "Error: %s attempted to start matchmaking, but did not have enough balance" % (user.title)
                        url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                        discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)

                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = '%s has insufficient balance' %team_member_user_record.title
                    )

                ## get this team_member's Game player
                team_member_game_player = gpController.get_by_gameKeyId_userKeyId(int(gameKeyId), team_member.userKeyId)
                if not team_member_game_player:
                    logging.info('%s had an error with the game player record' %team_member_user_record.title)
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = '%s had an error with the game player record' %team_member_user_record.title
                    )
                ## Check to see if characters are enabled, and get currently selected character if they are.
                if game.characters_enabled:
                    logging.info('characters are enabled.')
                    if team_member_game_player.characterCurrentKeyId:
                        logging.info('this team member has a characterCurrentKeyId')
                        game_character = gameCharacterController.get_by_key_id(team_member_game_player.characterCurrentKeyId)
                        if not game_character:
                            logging.info('game character not found')
                            return self.render_json_response(
                                authorization = True,
                                response_successful = False,
                                response_message = '%s has a character selected, but the record could not be found.' %team_member_user_record.title
                            )
                        if game_character.rank:
                            team_rank_total = team_rank_total + game_character.rank
                        else:
                            team_rank_total = team_rank_total + 1600

                        if game_character.score:
                            team_score_total = team_score_total + game_character.score

                        if game_character.experience:
                            team_exp_total = team_exp_total + game_character.experience
                        else:
                            team_exp_total = team_exp_total
                    else:
                        logging.info('This team member did not have a character selected.')
                        return self.render_json_response(
                            authorization = True,
                            response_successful = False,
                            response_message = '%s does not have an active character' %team_member_user_record.title
                        )
                else:
                    logging.info('characters are disabled')

                    team_rank_total = team_rank_total + team_member_game_player.rank
                    team_score_total = team_score_total + team_member_game_player.score
                    if team_member_game_player.experience:
                        team_exp_total = team_exp_total + team_member_game_player.experience
                    else:
                        team_exp_total = team_exp_total

                ## Use the captain's region.
                if team_member.captain:
                    logging.info('using the captain region')
                    mm_search_region = team_member_user_record.region


                ## TODO - clear out any existing placeholders for the team members


            ## team_average_rank
            mm_search_rank = team_rank_total / len(all_team_members)
            mm_search_score = team_score_total / len(all_team_members)
            mm_search_exp = team_exp_total / len(all_team_members)

            ## use this in metamode
            current_user_team_member_team_key_id = current_user_team_member.key.id()



        else:
            logging.info("Single player - No team found")

            ## Check current team size against the game mode's minimum and maximum
            if game_mode.teamSizeMin:
                if game_mode.teamSizeMin > 1:
                    logging.info('team size is lower than game_mode.teamSizeMin')
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = "Not enough players in the party for this game mode."
                    )

            ## create a new team, and team member.  We need it later.
            if user.defaultTeamTitle:
                title = user.defaultTeamTitle
            else:
                title = user.title + "'s Team"

            team = teamController.create(
                title = title,
                description = "created via matchmaker start",
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

            ## check for characters enabled and get the active character
            ## set up return values for either case - defaults in case they are not set for some reason
            mm_search_rank = game_player.rank or 1400
            mm_search_score = game_player.score or 0
            mm_search_exp = game_player.experience or 0
            mm_search_region = user.region

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
                    ## OK to go
                    mm_search_rank = game_character.rank
                    mm_search_score = game_character.score
                    mm_search_exp = game_character.experience
                    #mm_search_region = user.region
                else:
                    logging.info('You did not have a character selected.')
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = 'You do not have an active character'
                    )


            team_player = teamMembersController.create(
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


            ## Check to see if there are any existing pending matches for this user
            ## Check the gametype to see if they are still looking for a match or got disconnected.
            ## If the gametype is different, we need to close out the old match player and match if it exists, so we can create a new one.

            existing_match_player  = mpController.get_join_pending_by_gameKeyId_userKeyId(game_player.gameKeyId, user.key.id())
            if (existing_match_player):
                logging.info('found a joinable match player')
                if existing_match_player.matchmakerMode == matchtype:
                    logging.info('existing record matchtype is the same.  Aborting new match creation.')

                    if game.discord_subscribe_errors and game.discord_webhook_admin:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "Warning: %s attempted to start matchmaking, but an existing matchmaker record already exists for the chosen game mode.  Ignoring it - matchmaker check will find it." % (user.title)
                        url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                        discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)

                    ## matchmaker check will find it
                    return self.render_json_response(
                        authorization = True,
                        response_successful = True,
                        ## TODO let the player know they already have a match waiting
                        #servers = servers_response
                    )
                else:
                    logging.info('match type is different')

                    if existing_match_player.matchmakerMode == 'metamode':
                        logging.info('matchmaker was meta mode')
                        ## TODO deal with this and notify metagame if it's not metagame anymore.


            ## make sure the user has enough CRED to cover the admission fee set in gamemodes.
            logging.info('game_mode.admissionFeePerPlayer: %s '% game_mode.admissionFeePerPlayer )
            logging.info('user.currencyBalance: %s '% user.currencyBalance )

            if game_mode.admissionFeePerPlayer > user.currencyBalance:
                logging.info('user has insufficient balance')

                textMessage = "> Your balance of %s is insufficient to join this match type" % user.currencyBalance

                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
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
                    headers = {"Content-Type": "application/json"}
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

                if game.discord_subscribe_errors and game.discord_webhook_admin:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Error: %s attempted to start matchmaking, but did not have enough balance" % (user.title)
                    url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                    discord_data = { "embeds": [{"title": "Error", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "you do not have sufficient balance to start matchmaking for this game mode."
                )

            ## use this in metamode
            current_user_team_member_team_key_id = None

        ## TODO - clear out any existing placeholders for the user


        ## Branch on matchmaker type
        ## we need separate behavior for metaGame
        ## - contact the metagame backend and put all of the team into matchmaker started.  No tasks used here.
        if game_mode.matchmakerAlgorithm == "regionalRank":
            mm_search_value=mm_search_rank
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        elif game_mode.matchmakerAlgorithm == "regionalScore":
            mm_search_value=mm_search_score
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        elif game_mode.matchmakerAlgorithm == "regionalExperience":
            mm_search_value=mm_search_exp
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        elif game_mode.matchmakerAlgorithm == "globalRank":
            mm_search_value=mm_search_rank
            mm_search_region=None
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        elif game_mode.matchmakerAlgorithm == "globalScore":
            mm_search_value=mm_search_score
            mm_search_region=None
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        elif game_mode.matchmakerAlgorithm == "globalExperience":
            mm_search_value=mm_search_exp
            mm_search_region=None
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        elif game_mode.matchmakerAlgorithm == "metaGame":
            mm_search_value=mm_search_rank
            matchmakerAlgorithm = game_mode.matchmakerAlgorithm
        else:
            logging.info('no matchmakerAlgorithm found that matches, or was not selected')
            mm_search_value=mm_search_rank
            matchmakerAlgorithm = "regionalRank"

        if matchmakerAlgorithm == "metaGame":
            logging.info('found a metagame matchmaker request - checking with external API')

            ## Do this in a task maybe?  Possible timeouts from external APIs
            if not game.match_metagame_api_url:
                logging.info('game match_metagame_api_url not set up.  Cannot start metaGame MM')
                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "game match_metagame_api_url not set up.  Cannot start metaGame MM."
                )

            ## get this player's group details
            #groupController = GroupsController()
            #groupRoleController = GroupRolesController()
            #groupUserController = GroupUsersController()
            #groupGameController = GroupGamesController()

            ## First make sure the user even has a group selected
            if not user.groupTagKeyId:
                logging.info('user does not have a group selected.')

                # push out to in-game clients via heroku
                textMessage = "> Group membership is required for metagame.  Create or join a group on the uetopia groups page. "
                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
                                        "userKeyId": "SYSTEM",
                                        "userTitle": "SYSTEM",
                                        "created":datetime.datetime.now().isoformat()
                })
                # ignore if it's failing
                try:
                    headers = {"Content-Type": "application/json"}
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

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "Groups are required for metagame.  Select your group in your uetopia profile first."
                )

            ## make sure the group is connected to this game
            group_game = groupGameController.get_by_groupKeyId_gameKeyId(user.groupTagKeyId, game.key.id())
            if not group_game:
                logging.info('The group is not connected to this game.')

                # push out to in-game clients via heroku
                textMessage = "> The group is not connected to this game.  "
                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
                                        "userKeyId": "SYSTEM",
                                        "userTitle": "SYSTEM",
                                        "created":datetime.datetime.now().isoformat()
                })
                # ignore if it's failing
                try:
                    headers = {"Content-Type": "application/json"}
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

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "The group is not connected to this game.  Connect the game first."
                )

            ## get the group member so that we can get the role associated.
            group_member = groupUserController.get_by_groupKeyId_userKeyId(user.groupTagKeyId, user.key.id())
            if not group_member:
                logging.info('The group member could not be found.')
                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "The group member record could not be found.  Re-select your group in your profile."
                )

            ## get the group member's role
            group_member_role = groupRoleController.get_by_key_id(group_member.roleKeyId)
            if not group_member_role:
                logging.info('The group member role could not be found.')

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "The group member role could not be found.  Re-select your group in your profile."
                )

            ## Lastly, make sure they have at least team lead permission
            if not group_member_role.metagame_team_lead:
                logging.info('The group member does not have metagame_team_lead permission.')

                # push out to in-game clients via heroku
                textMessage = "> You do not have the metagame_team_lead permission for this group. "
                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
                                        "userKeyId": "SYSTEM",
                                        "userTitle": "SYSTEM",
                                        "created":datetime.datetime.now().isoformat()
                })
                # ignore if it's failing
                try:
                    headers = {"Content-Type": "application/json"}
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

                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "You do not have metagame_team_lead permission.  Request this permission from a group officer or leader."
                )

            ## get the group so we can update the tag and icon
            group = groupController.get_by_key_id(group_member.groupKeyId)
            if not group:
                return self.render_json_response(
                    authorization = True,
                    response_successful = False,
                    response_message = "The group was not found."
                )


            uri = "/api/v1/metagame/player_start"

            group_tag = "[" + group.tag + "]"

            ## send params as json.
            json_params = OrderedDict([
                ("nonce", time.time()),
                ("player_key_id", game_player.key.id()),
                ("team_key_id", current_user_team_member_team_key_id),
                ("team_captain", True),
                ("team_title", user.defaultTeamTitle),
                ("group_key_id", user.groupTagKeyId),
                ("group_tag", group_tag),
                ("group_icon_serving_url", group.iconServingUrl),
                ("metagame_team_lead", group_member_role.metagame_team_lead),
                ("metagame_faction_lead", group_member_role.metagame_faction_lead),
            ])

            json_encoded = json.dumps(json_params)

            # Hash the params string to produce the Sign header value
            H = hmac.new(str(game.apiSecret), digestmod=hashlib.sha512)
            H.update(json_encoded)
            sign = H.hexdigest()

            headers = {"Content-type": "application/x-www-form-urlencoded",
                               "Key":game.apiKey,
                               "Sign":sign}

            conn = httplib.HTTPSConnection(game.match_metagame_api_url)

            ## This can totally fail.  But it should be ok.
            try:
                conn.request("POST", uri, json_encoded, headers)
                response = conn.getresponse()

                #logging.info(response.read())

                ## parse the response
                jsonstring = str(response.read())
                logging.info(jsonstring)
                jsonobject = json.loads(jsonstring)

                # do something with the response
                if not jsonobject['request_successful']:
                    logging.info('the metagame API request was unsuccessful')

                    return self.render_json_response(
                        response_message='MetaGame API request failed.',
                        response_successful=False
                    )

                logging.info('validation was successful')
            except:
                logging.error('metagame API request failed or timed out.')


            ## this is just an unused placeholder it gets set later
            matchTaskStatusKeyId = None

        else:
            logging.info('not a metagame matchmaker request.  looking for tasks')
            logging.info("mm_search_region: %s" % mm_search_region)

            possible_matchmaker_tasks = mtsController.get_list_by_game_algorithm_region_mode_rankMin(game_mode.gameKeyId, matchmakerAlgorithm, mm_search_region, matchtype, mm_search_value)

            found_matchmaker_task = False
            match_task_status = None
            for p_mm_task in possible_matchmaker_tasks:
                if p_mm_task.rankMax >= mm_search_value:
                    logging.info('found matchmaker task that fits the parameters requested')
                    logging.info('found matchmaker task keyId: %s' % p_mm_task.key.id() )
                    found_matchmaker_task = True
                    match_task_status = p_mm_task
                    break

            if game_mode.matchmakerDisparityMax:
                matchmakerDisparityMax = game_mode.matchmakerDisparityMax
            else:
                matchmakerDisparityMax = MATCHMAKER_RANK_MARGIN


            if not found_matchmaker_task:
                logging.info('no matchmaker task was found that is compatible.  Starting a new one')

                ## TODO - get the webhook for this region from the game.
                ## if the global setting to subscribe is false, don't push anything.
                discord_subscribe = game.discord_subscribe_matchmaker_task_status
                discord_webhook = ""

                if mm_search_region == "na-northeast1":
                    discord_webhook = game.discord_webhook_na_northeast1
                elif mm_search_region == "us-central1":
                    discord_webhook = game.discord_webhook_us_central1
                elif mm_search_region == "us-west1":
                    discord_webhook = game.discord_webhook_us_west1
                elif mm_search_region == "us-west2":
                    discord_webhook = game.discord_webhook_us_west2

                elif mm_search_region == "us-west3":
                    discord_webhook = game.discord_webhook_us_west3
                elif mm_search_region == "us-west4":
                    discord_webhook = game.discord_webhook_us_west4

                elif mm_search_region == "us-east4":
                    discord_webhook = game.discord_webhook_us_east4
                elif mm_search_region == "us-east1":
                    discord_webhook = game.discord_webhook_us_east1
                elif mm_search_region == "southamerica-east1":
                    discord_webhook = game.discord_webhook_southamerica_east1
                elif mm_search_region == "europe-north1":
                    discord_webhook = game.discord_webhook_europe_north1
                elif mm_search_region == "europe-west1":
                    discord_webhook = game.discord_webhook_europe_west1
                elif mm_search_region == "europe-west2":
                    discord_webhook = game.discord_webhook_europe_west2
                elif mm_search_region == "europe-west3":
                    discord_webhook = game.discord_webhook_europe_west3
                elif mm_search_region == "europe-west4":
                    discord_webhook = game.discord_webhook_europe_west4

                elif mm_search_region == "europe-west6":
                    discord_webhook = game.discord_webhook_europe_west6

                elif mm_search_region == "asia-south1":
                    discord_webhook = game.discord_webhook_asia_south1
                elif mm_search_region == "asia-southeast1":
                    discord_webhook = game.discord_webhook_asia_southeast1
                elif mm_search_region == "asia-east1":
                    discord_webhook = game.discord_webhook_asia_east1

                elif mm_search_region == "asia-east2":
                    discord_webhook = game.discord_webhook_asia_east2

                elif mm_search_region == "asia-northeast1":
                    discord_webhook = game.discord_webhook_asia_northeast1

                elif mm_search_region == "asia-northeast2":
                    discord_webhook = game.discord_webhook_asia_northeast2
                elif mm_search_region == "asia-northeast3":
                    discord_webhook = game.discord_webhook_asia_northeast3

                elif mm_search_region == "australia-southeast1":
                    discord_webhook = game.discord_webhook_australia_southeast1
                else:
                    discord_subscribe = False

                logging.info("mm_search_region: %s" % mm_search_region)

                match_task_status = mtsController.create(
                    gameKeyId = game_player.gameKeyId,
                    gameTitle = game_player.gameTitle,
                    region = mm_search_region,
                    mode = matchtype,
                    rankMin = mm_search_value - matchmakerDisparityMax,
                    rankMedian = mm_search_value,
                    rankMax = mm_search_value + matchmakerDisparityMax,
                    matchmakerAlgorithm = matchmakerAlgorithm,
                    successful_runs = 0,
                    successful_match_count = 0,
                    failed_runs = 0,
                    consecutive_failed_runs = 0,
                    discord_subscribe = discord_subscribe,
                    discord_webhook = discord_webhook

                )
                ##  start the task to deal with it.
                taskUrl='/task/game/match/queue/process'
                taskqueue.add(url=taskUrl, queue_name='gameMatchQueueProcess', params={'key_id': match_task_status.key.id()}, countdown = 2,)

            matchTaskStatusKeyId = match_task_status.key.id()

        if current_user_team_member:
            ## Process all team members
            for team_member in all_team_members:
                match_player = mpController.get_pending_by_gameKeyId_userKeyId(int(gameKeyId), team_member.userKeyId)

                team_member_user_record = userController.get_by_key_id(team_member.userKeyId)

                if team_member_user_record.groupTag:
                    team_member_user_record_title = team_member_user_record.groupTag + " " + team_member_user_record.title
                else:
                    team_member_user_record_title = team_member_user_record.title

                team_member_game_player = gpController.get_by_gameKeyId_userKeyId(int(gameKeyId), team_member.userKeyId)

                this_player_rank = team_member_game_player.rank

                ## check for character and get character
                ## keep track of customized state
                characterCustomized = False
                if game.characters_enabled:
                    logging.info('characters are enabled.')
                    if team_member_game_player.characterCurrentKeyId:
                        logging.info('this team_member_game_player has a characterCurrentKeyId')
                        game_character = gameCharacterController.get_by_key_id(team_member_game_player.characterCurrentKeyId)
                        if not game_character:
                            logging.info('game character not found')
                            return self.render_json_response(
                                authorization = True,
                                response_successful = False,
                                response_message = 'team member character could not be found.'
                            )
                        ## check to see if this character has been updated or not
                        if game_character.characterState == "customized":
                            characterCustomized = True
                        ## OK to go
                        if team_member_user_record.groupTag:
                            team_member_user_record_title = team_member_user_record.groupTag + " " + game_character.title
                        else:
                            team_member_user_record_title = game_character.title

                        this_player_rank = game_character.rank
                    else:
                        logging.info('You did not have a character selected.')
                        return self.render_json_response(
                            authorization = True,
                            response_successful = False,
                            response_message = 'You do not have an active character'
                        )


                if not match_player:
                    logging.info('no match player found, creating a new one.')


                    match_player = mpController.create(
                        userKeyId = team_member_user_record.key.id(),
                        userTitle = team_member_user_record_title,
                        firebaseUser = team_member_user_record.firebaseUser,
                        gameKeyId = int(gameKeyId),
                        teamKeyId = team_member.teamKeyId,
                        teamTitle = team_member.teamTitle,
                        teamCaptain = team_member.captain,

                        ## TODO - identify the flags we're not using and delete them.
                        joined = False,
                        committed = False,
                        approved = False,
                        left = False,
                        verified = False,
                        blocked = False,

                        ## matchmaker stuff
                        matchmakerStarted = True,
                        matchmakerPending = True,
                        matchTaskStatusKeyId = matchTaskStatusKeyId,
                        matchmakerFoundMatch = False,
                        matchmakerServerReady = False,
                        matchmakerFinished = False,
                        matchmakerJoinable = False,
                        matchmakerJoinPending = True,
                        matchmakerMode = matchtype,
                        matchmakerUserRegion = team_member_user_record.region,

                        rank = this_player_rank,
                        score =0, ## score is set to zero on the start of each match and tallied on the backend on matchresults.
                        gamePlayerKeyId = team_member_game_player.key.id(),

                        defaultTeamTitle = team_member_user_record.defaultTeamTitle,
                        groupTag = team_member_user_record.groupTag,
                        groupTagKeyId = team_member_user_record.groupTagKeyId,
                        characterCustomized = characterCustomized,

                        twitch_channel_id = team_member_user_record.twitch_channel_id,
                        twitch_currently_streaming = team_member_user_record.twitch_currently_streaming,

                        stale = stale_timestamp,
                        stale_requires_check = True,

                    )
                else:
                    match_player.matchmakerStarted = True
                    match_player.matchmakerPending = True
                    match_player.matchmakerJoinPending = True
                    match_player.matchTaskStatusKeyId = matchTaskStatusKeyId
                    match_player.defaultTeamTitle = user.defaultTeamTitle
                    match_player.groupTag = user.groupTag
                    match_player.groupTagKeyId = user.groupTagKeyId
                    match_player.rank = this_player_rank
                    match_player.userTitle = team_member_user_record_title

                    match_player.twitch_channel_id = team_member_user_record.twitch_channel_id
                    match_player.twitch_currently_streaming = team_member_user_record.twitch_currently_streaming

                    match_player.stale = stale_timestamp
                    match_player.stale_requires_check = True
                    mpController.update(match_player)



                push_payload = {'matchType': matchtype}

                payload_json = json.dumps(push_payload)

                #try:
                headers = {"Content-Type": "application/json"}
                URL = "%s/user/%s/matchmaker/started" % (HEROKU_SOCKETIO_SERVER, match_player.firebaseUser)
                resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      payload_json,
                                      headers=headers)

                logging.info(resp)
                logging.info(content)

                ## For the Legacy OSS we need some special handling here
                ## It does not include "OnMatchmakerStarted" so we cannot inform players that are in a party that the captain has started matchmaking.
                ## Instead, we are going to send out a chat message

                textMessage = "> %s matchmaker started" %matchtype

                chat_msg = json.dumps({"type":"chat",
                                        "textMessage":textMessage,
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
                    headers = {"Content-Type": "application/json"}
                    URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, match_player.firebaseUser)
                    resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      chat_msg,
                                      headers=headers)

                    logging.info(resp)
                    logging.info(content)
                except:
                    logging.error('heroku error')

        else:
            ## Process single user

            ## update the match player with the match settings
            match_player = mpController.get_pending_by_gameKeyId_userKeyId(int(gameKeyId), userid)

            ## we already have game player
            ## get the character if enabled
            this_player_rank = game_player.rank
            if user.groupTag:
                user_title = user.groupTag + " " + user.title
            else:
                user_title = user.title

            ## keep track of customized state
            characterCustomized = False

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
                            response_message = 'team member character could not be found.'
                        )
                    ## check to see if this character has been updated or not
                    if game_character.characterState == "customized":
                        characterCustomized = True

                    ## OK to go
                    if user.groupTag:
                        user_title = user.groupTag + " " + game_character.title
                    else:
                        user_title = game_character.title

                    this_player_rank = game_character.rank
                else:
                    logging.info('You did not have a character selected.')
                    return self.render_json_response(
                        authorization = True,
                        response_successful = False,
                        response_message = 'You do not have an active character'
                    )

            if not match_player:
                logging.info('no match player found, creating a new one.')



                match_player = mpController.create(
                    userKeyId = user.key.id(),
                    userTitle = user_title,
                    firebaseUser = user.firebaseUser,
                    gameKeyId = int(gameKeyId),

                    ## TODO - identify the flags we're not using and delete them.
                    joined = False,
                    committed = False,
                    approved = False,
                    left = False,
                    verified = False,
                    blocked = False,

                    ## matchmaker stuff
                    matchmakerStarted = True,
                    matchmakerPending = True,
                    matchTaskStatusKeyId = matchTaskStatusKeyId,
                    matchmakerFoundMatch = False,
                    matchmakerServerReady = False,
                    matchmakerFinished = False,
                    matchmakerJoinable = False,
                    matchmakerJoinPending = True,
                    matchmakerMode = matchtype,
                    matchmakerUserRegion = user.region,

                    rank = this_player_rank,
                    score = 0, ## score is set to zero on the start of each match and tallied on the backend on matchresults.
                    gamePlayerKeyId = game_player.key.id(),
                    defaultTeamTitle = user.defaultTeamTitle,
                    groupTag = user.groupTag,
                    groupTagKeyId = user.groupTagKeyId,
                    characterCustomized = characterCustomized,

                    twitch_channel_id = user.twitch_channel_id,
                    twitch_currently_streaming = user.twitch_currently_streaming,

                    stale = stale_timestamp,
                    stale_requires_check = True
                )
            else:
                match_player.matchmakerStarted = True
                match_player.matchmakerPending = True
                match_player.matchmakerJoinPending = True
                match_player.matchTaskStatusKeyId = match_task_status.key.id()
                match_player.defaultTeamTitle = user.defaultTeamTitle
                match_player.groupTag = user.groupTag
                match_player.groupTagKeyId = user.groupTagKeyId
                match_player.rank = this_player_rank
                match_player.userTitle = user_title
                match_player.twitch_channel_id = user.twitch_channel_id
                match_player.twitch_currently_streaming = user.twitch_currently_streaming
                match_player.stale = stale_timestamp
                match_player.stale_requires_check = True
                mpController.update(match_player)

            textMessage = "> %s matchmaker started" %matchtype

            chat_msg = json.dumps({"type":"chat",
                                    "textMessage":textMessage,
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
                headers = {"Content-Type": "application/json"}
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


        return self.render_json_response(
            authorization = True,
            success = True,
            #servers = servers_response
        )
