import endpoints
import logging
import uuid
import urllib
import json
import copy
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from httplib2 import Http
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.handlers import BaseHandler
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.match_task_status import MatchTaskStatusController

from apps.uetopia.controllers.match_teams import MatchTeamsController
#from apps.uetopia.controllers.match_team_players import MatchTeamPlayersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.providers.compute_engine_zonemap import region_zone_mapper

from configuration import *

class MatchQueueProcessHandler(BaseHandler):
    def get_teammate_count(self, pending_match_players, teamKeyId):
        logging.info("getting pending teammates")
        count = 0
        for pending_match_player in pending_match_players:
            if pending_match_player.teamKeyId == teamKeyId:
                count = count +1
        return count


    def post(self):
        logging.info("[TASK] MatchQueueProcessHandler")

        ## get the match task status record
        ## search for players that have indicated themselves as part of this task.  matchTaskStatusKeyId
        ## loop through all the players, and put them in new matches
        ## update the match status task
        ## if there are more players pending, requeue the task
        ## if nothing is happening for too long, delete the task status

        ## this is a match status key
        key_id = self.request.get('key_id')
        logging.info(key_id)

        mtsController = MatchTaskStatusController()
        mpController = MatchPlayersController()
        gmController = GameModesController()
        mController = MatchController()
        gameController = GamesController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()
        teamsController = TeamsController()
        teamMembersController = TeamMembersController()
        matchTeamController = MatchTeamsController()
        #matchTeamPlayerController = MatchTeamPlayersController()

        match_task_status = mtsController.get_by_key_id(int(key_id))
        if not match_task_status:
            logging.error('match task status was not found!')
            return

        matches_created = 0



        ## get the game mode
        game_mode = gmController.get_by_gameKeyId_onlineSubsystemReference(match_task_status.gameKeyId, match_task_status.mode)
        if not game_mode:
            logging.error('game mode not found')
            return

        pending_players, cursor, more = mpController.list_page_pending_by_matchTaskStatusKeyId_descending(match_task_status.key.id())
        len_pending_players = len(pending_players)
        logging.info('Task found %s pending match players' %len_pending_players)

        ## first just a simple check to see if there are even enough players to continue with more logic
        if len(pending_players) > 0:
            if len(pending_players) < game_mode.playersPerTeam * game_mode.teams:
                logging.info('not enough players in the queue to fill a match')

                ## send an alert out to discord - if configured
                if match_task_status.discord_subscribe:
                    try:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "[ %s ] [ %s %s %s ] [ Matches found: %s ] [ In Queue: %s ] Checking again in %s seconds" %(match_task_status.mode, match_task_status.rankMin,
                                                                                                                        match_task_status.rankMedian,
                                                                                                                        match_task_status.rankMax, matches_created, len_pending_players, MATCHMAKER_QUEUE_PROCESS_REQUEUE_LEFTOVER_SECONDS)
                        url = "http://ue4topia.appspot.com/#/game/%s" % match_task_status.gameKeyId
                        discord_data = { "embeds": [{"title": "Matchmaker Status", "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(match_task_status.discord_webhook,
                                          "POST",
                                          data,
                                          headers=headers)
                    except:
                        logging.info('Discord push fail')

                ## requeue the task
                taskUrl='/task/game/match/queue/process'
                taskqueue.add(url=taskUrl, queue_name='gameMatchQueueProcess', params={'key_id': match_task_status.key.id()}, countdown = MATCHMAKER_QUEUE_PROCESS_REQUEUE_LEFTOVER_SECONDS,)
                return


        ## get the game
        game = gameController.get_by_key_id(match_task_status.gameKeyId)
        if not game:
            logging.error('game not found')
            return

        ## deep copy a list for pre-processing
        pending_players_preprocess = copy.deepcopy(pending_players)

        # We need to determine if any players are grouped together.  They should end up on the same team.

        ## TODO redo this.
        ## It should be more comprehensive not just filling teams
        # 1 figure out how many matches we can fill, which gives us the number of teams we need
        # 2 Prioritize teams with multiple players
        # 3 prioritize players that have been waiting
        # 4 Get the average skill/rank/score from the players that were chosen
        # 5 figure out the new teams, keeping previously grouped players together trying to get as close to the average as possible

        # 1 how many matches can we fill
        number_of_matches_that_can_be_filled = int( len(pending_players) / game_mode.playersPerTeam / game_mode.teams)
        number_of_teams_required = number_of_matches_that_can_be_filled * game_mode.teams

        logging.info('number_of_matches_that_can_be_filled: %s ' %number_of_matches_that_can_be_filled)
        logging.info('number_of_teams_required: %s ' %number_of_teams_required)




        full_teams = []
        team_fill_incomplete = False
        # First pass, we'll get all of the team members, and do initial flagging
        for match_player_primary_index, match_player_primary in enumerate(pending_players_preprocess):
            team_members_temp = []
            if match_player_primary.teamKeyId:
                logging.info('primary is on a team!')


                ## prevent duplicates
                if not match_player_primary.matchmaker_team_assignment_in_progress:

                    ## set primary assignment in progress to true
                    match_player_primary.matchmaker_team_assignment_in_progress = True
                    team_members_temp.append(match_player_primary)

                    ## find all of the other members of the team
                    team_size = 1
                    for match_player_secondary_index, match_player_secondary in enumerate(pending_players_preprocess):
                        ## prevent duplicates - We need to eliminate primary with this
                        if not match_player_secondary.matchmaker_team_assignment_in_progress:
                            if match_player_secondary.teamKeyId:
                                logging.info('secondary is on a team')
                                if match_player_secondary.teamKeyId == match_player_primary.teamKeyId:
                                    logging.info('secondary is on THIS team')
                                    match_player_secondary.matchmaker_team_assignment_in_progress = True
                                    match_player_secondary.index = match_player_secondary_index

                                    #if match_player_primary.key.id() !=  match_player_secondary.key.id():
                                    ## skip the primary!
                                    team_size = team_size + 1
                                    team_members_temp.append(match_player_secondary)
                    ## If it's full, just add it to the team list.
                    logging.info('team_size 1: %s' %team_size)
                    logging.info('playersPerTeam 1: %s' %game_mode.playersPerTeam)
                    if team_size == game_mode.playersPerTeam:
                        full_teams.append(team_members_temp)
                    else:
                        logging.info('The team is assembled, but its not enough to satisfy the MM team size' )
                        ## Fill with singles

                        ## This is a problem because players will usually be on a team of 1

                        # we shouldn't build out the team here anyway???

                        for match_player_tertiary_index, match_player_tertiary in enumerate(pending_players_preprocess):
                            if team_size < game_mode.playersPerTeam:
                                logging.info('the team still needs more players')
                                if not match_player_tertiary.teamKeyId:
                                    logging.info('the player is NOT on a team!')

                                    ## prevent duplicates
                                    if not match_player_tertiary.matchmaker_team_assignment_in_progress:

                                        match_player_tertiary.matchmaker_team_assignment_in_progress = True
                                        match_player_tertiary.index = match_player_tertiary_index
                                        team_size = team_size + 1
                                        team_members_temp.append(match_player_tertiary)
                                        ## remove the record from our preprocess list?

                                else:
                                    logging.info('the player is on a team')

                                    ## check to see if this entire team will fit
                                    ## we already have the data in memory.  DOn't do another DB lookup
                                    #filling_team_players = teamMembersController.get_by_teamKeyId(match_player_tertiary.teamKeyId)

                                    ## The entire team should already be in the queue - TODO double check
                                    team_players_needed = game_mode.playersPerTeam - team_size
                                    team_player_count = self.get_teammate_count(pending_players_preprocess, match_player_tertiary.teamKeyId)

                                    if team_player_count <= team_players_needed:
                                        logging.info('this team will fit')

                                        ## add them all to the team
                                        for match_player_other_team_member_index, match_player_other_team_member in enumerate(pending_players_preprocess):
                                            # only if they are on the team
                                            if match_player_other_team_member.teamKeyId == match_player_tertiary.teamKeyId:
                                                logging.info('found this other team member')
                                                ## prevent duplicates
                                                if not match_player_other_team_member.matchmaker_team_assignment_in_progress:
                                                    logging.info('adding this other team member')
                                                    match_player_other_team_member.matchmaker_team_assignment_in_progress = True
                                                    match_player_other_team_member.index = match_player_other_team_member_index
                                                    team_size = team_size + 1
                                                    team_members_temp.append(match_player_other_team_member)


                        ## verify team size
                        logging.info('team_size 2: %s' %team_size)
                        logging.info('playersPerTeam 2: %s' %game_mode.playersPerTeam)
                        if team_size == game_mode.playersPerTeam:
                            full_teams.append(team_members_temp)
                        else:
                            logging.info('the team was assembled and filled, but was not enough to satisfy the MM team size.')
                            team_fill_incomplete = True
            else:
                logging.info('primary is not on a team -1')

        ## do the leftover singles afterwords.
        for match_player_primary_index, match_player_primary in enumerate(pending_players_preprocess):
            team_members_temp = []
            if not match_player_primary.teamKeyId:
                logging.info('primary is not on a team -2')
                if not match_player_primary.matchmaker_team_assignment_in_progress:
                    logging.info('primary %s has not been processed yet' %match_player_primary.userTitle)
                    ## Start a new team beginning with the primary
                    match_player_primary.matchmaker_team_assignment_in_progress = True
                    match_player_primary.index = match_player_primary_index
                    team_members_temp.append(match_player_primary)
                    ## fill with singles
                    team_size = 1
                    for match_player_secondary_index, match_player_secondary in enumerate(pending_players_preprocess):
                        logging.info('checking secondary: %s' %match_player_secondary.userTitle)
                        if team_size < game_mode.playersPerTeam:
                            logging.info('still room on this team')
                            if not match_player_secondary.teamKeyId:
                                logging.info('secondary is not on a team')

                                if not match_player_secondary.matchmaker_team_assignment_in_progress:
                                    logging.info('secondary is not matchmaker_team_assignment_in_progress, adding to the team')
                                    match_player_secondary.matchmaker_team_assignment_in_progress = True
                                    match_player_secondary.index = match_player_secondary_index
                                    team_members_temp.append(match_player_secondary)
                                    team_size = team_size + 1
                        else:
                            logging.info('secondary team fill complete - breaking out')
                            break
                    ## verify team size
                    if team_size == game_mode.playersPerTeam:
                        full_teams.append(team_members_temp)
                    else:
                        logging.info('the team was assembled and filled with %s, but was not enough to satisfy the MM team size of %s.' %( team_size, game_mode.playersPerTeam))
                        team_fill_incomplete = True

        ## Calculate the team average rank
        team_rank_averages = []
        for team_index, team_temp in enumerate(full_teams):
            team_rank_total = 0
            team_rank_divisor = 0
            for team_player_temp in team_temp:
                if team_player_temp.rank:
                    team_rank_total = team_rank_total + team_player_temp.rank
                else:
                    team_rank_total = team_rank_total + 1600
                team_rank_divisor = team_rank_divisor + 1

            if team_rank_divisor:
                team_rank_average = team_rank_total / team_rank_divisor
            else:
                logging.info('No team rank divisor')
                team_rank_average = 1600 ## this shouldn't happen
            team_rank_averages.append(team_rank_average)

        ## TODO sort them
        #https://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list

        ## Go through the team array we just set up and build out the match and match players


        while (len(full_teams) >= game_mode.teams ):
            logging.info('there are enough full teams to fill a match')

            matchTitle = match_task_status.gameTitle + " : " + game_mode.onlineSubsystemReference

            ## check to see if localtesting is enabled.
            if game.match_deploy_vm_local_testing:
                logging.info('match_deploy_vm_local_testing TRUE')

                ## Set up the match using the developer specified preset values.
                match = mController.create(
                    gameKeyId = match_task_status.gameKeyId,
                    #gameTitle = ndb.StringProperty(indexed=False)
                    playersPerTeam = match_task_status.playersPerTeam,
                    teams = match_task_status.teams,
                    continuous_server_region = match_task_status.region,
                    apiKey = game.match_deploy_vm_local_APIKey,
                    apiSecret = game.match_deploy_vm_local_APISecret,
                    title = matchTitle,
                    admissionFee = 0,
                    gameModeKeyId = game_mode.key.id(),
                    gameModeTitle = game_mode.onlineSubsystemReference,
                    ## TODO add match initialization settings
                    continuous_server_zone = "localtesting",
                    continuous_server_machine_type = game.match_deploy_vm_machine_type,
                    admissionFeePerPlayer = game_mode.admissionFeePerPlayer,
                    winRewardPerPlayer = game_mode.winRewardPerPlayer,

                    match_title = 'localtesting',
                    hostConnectionLink = game.match_deploy_vm_local_testing_connection_string,

                    match_creating = False,
                    match_provisioned = True,
                    match_active = True,
                    continuous_server_project = "locatesting",
                )


            else:
                logging.info('match_deploy_vm_local_testing FALSE')
                ## build the match so we can get a matchKeyId

                ## global matchmaker needs a region
                region = None
                if match_task_status.region:
                    logging.info('found region in match task status')
                    region = match_task_status.region
                else:
                    logging.info('no region found in match task status')
                    for playerdata in full_teams[0]:
                        if playerdata.teamCaptain:
                            if playerdata.matchmakerUserRegion:
                                logging.info('found region from a team captain')
                                region = playerdata.matchmakerUserRegion
                                break
                if not region: # maybe there were no team captains?
                    logging.info('No region found by captain or match status')
                    for playerdata in full_teams[0]:
                        if playerdata.matchmakerUserRegion:
                            logging.info('found region by player')
                            region = playerdata.matchmakerUserRegion
                            break




                match = mController.create(
                    gameKeyId = match_task_status.gameKeyId,
                    gameTitle = game.title,
                    playersPerTeam = match_task_status.playersPerTeam,
                    teams = match_task_status.teams,

                    apiKey = mController.create_unique_api_key(),
                    apiSecret = mController.key_generator(),
                    title = matchTitle,
                    admissionFee = 0,
                    gameModeKeyId = game_mode.key.id(),
                    gameModeTitle = game_mode.onlineSubsystemReference,
                    ## TODO add match initialization settings

                    continuous_server_region = region,
                    continuous_server_zone = region_zone_mapper(region),
                    continuous_server_machine_type = game.match_deploy_vm_machine_type,
                    admissionFeePerPlayer = game_mode.admissionFeePerPlayer,
                    winRewardPerPlayer = game_mode.winRewardPerPlayer
                )

                ## TODO do we need any checks here?
                ## start a task to create the vm
                taskUrl='/task/matchmaker/vm/allocate'
                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={
                                                                                        "matchKeyId": match.key.id()
                                                                                    })
            #  We're still in the loop to create full games.
            # We want to loop over the number of teams needed to make a match (usually 2)
            # logging.info("full_teams: %s" %full_teams)

            #  full_teams: (1v1 example)
            #  [
            #  [
            #  MatchPlayers(key=Key('MatchPlayers', 5710682603388928), approved=False, blocked=False, committed=False, created=datetime.datetime(2017, 7, 16, 20, 32, 3, 863820), experience=None, firebaseUser=u'St4V4lmLxAUNTzRklK4pma5icHq2',
            #  gameKeyId=5748755743637504L, gamePlayerKeyId=5721185543258112L, gameTitle=None, hero=None, joined=False, left=False, matchKeyId=None, matchTaskStatusKeyId=5644230869385216L, matchTitle=None, matchmakerCheckUnusedProcessed=None,
            #  matchmakerFinished=False, matchmakerFoundMatch=False, matchmakerJoinPending=True, matchmakerJoinable=False, matchmakerMode=u'1v1', matchmakerPending=True, matchmakerServerReady=False, matchmakerStarted=True,
            #  matchmaker_team_assignment_in_progress=True, modified=datetime.datetime(2017, 7, 16, 20, 32, 3, 863840), playstyle_achiever=None, playstyle_explorer=None, playstyle_killer=None, playstyle_socializer=None, rank=1600, score=0,
            #  session_host_address=None, session_id=None, teamId=None, teamKeyId=None, teamTitle=None, userKeyId=5112991330598912L, userTitle=u'Ed-UEtopia', verified=False, weapon=None, win=None)
            #  ],
            #  [
            #  MatchPlayers(key=Key('MatchPlayers', 6278707865976832), approved=False, blocked=False, committed=False, created=datetime.datetime(2017, 7, 16, 20, 32, 1, 472610), experience=None, firebaseUser=u'GUhvMkh25hP7391mHxlBp6jlj563',
            #  gameKeyId=5748755743637504L, gamePlayerKeyId=5655778694266880L, gameTitle=None, hero=None, joined=False, left=False, matchKeyId=None, matchTaskStatusKeyId=5644230869385216L, matchTitle=None, matchmakerCheckUnusedProcessed=None,
            #  matchmakerFinished=False, matchmakerFoundMatch=False, matchmakerJoinPending=True, matchmakerJoinable=False, matchmakerMode=u'1v1', matchmakerPending=True, matchmakerServerReady=False, matchmakerStarted=True,
            #  matchmaker_team_assignment_in_progress=True, modified=datetime.datetime(2017, 7, 16, 20, 32, 1, 472640), playstyle_achiever=None, playstyle_explorer=None, playstyle_killer=None, playstyle_socializer=None, rank=1556, score=0,
            #  session_host_address=None, session_id=None, teamId=None, teamKeyId=None, teamTitle=None, userKeyId=5693417237512192L, userTitle=u'Ed Colmar', verified=False, weapon=None, win=None)
            #  ]
            #  ]

            ## Set up the match chat channels.
            ## We need one for the match
            ## And one for each team

            match_chat_title = "match chat"
            match_chat_channel = chatChannelController.create(
                title = match_chat_title,
                channel_type = 'match',
                #adminUserKeyId = authorized_user.key.id(),
                refKeyId = match.key.id(),
                gameKeyId = game.key.id(),
                max_subscribers = 200
            )


            for team_index in range(game_mode.teams):
                logging.info('processing team %s'% team_index)
                team_data_temp = full_teams.pop(0)  # don't pop the index, just take the bottom - since it's changing as they get deleted out

                ## get a team title from one of the players
                final_team_title = None
                for player_data_temp in team_data_temp:
                    logging.info('processing player for team title')
                    #logging.info(player_data_temp)

                    if not final_team_title:
                        ## team title not set
                        if player_data_temp.defaultTeamTitle:
                            final_team_title = player_data_temp.defaultTeamTitle
                        else:
                            final_team_title = "%s's Team" % player_data_temp.userTitle

                ## create the match_team record first.
                match_team = matchTeamController.create(
                    title = final_team_title,
                    matchKeyId = match.key.id(),
                    matchTitle = match.title,
                    gameKeyId = game.key.id(),
                    gameTitle = game.title,
                    teamIndex = team_index
                )



                ## set up the team chat channel
                if game_mode.playersPerTeam > 1:
                    match_chat_title = final_team_title + " team chat"

                    team_chat_channel = chatChannelController.create(
                        title = match_chat_title,
                        channel_type = 'matchteam',
                        refKeyId = match_team.key.id(),
                        gameKeyId = game.key.id(),
                        max_subscribers = 200
                    )

                #logging.info(team_data_temp)
                for player_data_temp in team_data_temp:
                    logging.info('processing player')
                    #logging.info(player_data_temp)

                    player_data_temp.matchmakerPending = False
                    player_data_temp.matchmakerFoundMatch = True
                    player_data_temp.teamId = team_index
                    if not player_data_temp.teamTitle:
                        player_data_temp.teamTitle = final_team_title
                    player_data_temp.matchKeyId = match.key.id()
                    player_data_temp.session_host_address = match.hostConnectionLink
                    player_data_temp.session_id = match.session_id
                    player_data_temp.matchTeamKeyId = match_team.key.id()
                    player_data_temp.matchTeamTitle = match_team.title

                    mpController.update(player_data_temp)


                    ####### MATCH CHAT CHANNEL ########
                    ## subscribe the player to the match chat_channel
                    ## Subscribe the player to it
                    subscriber = chatChannelSubscribersController.create(
                        online = True,
                        chatChannelKeyId = match_chat_channel.key.id(),
                        chatChannelTitle = match_chat_channel.title,
                        userKeyId = player_data_temp.userKeyId,
                        userTitle = player_data_temp.userTitle,
                        userFirebaseUser = player_data_temp.firebaseUser,
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
                            chatChannelKeyId = team_chat_channel.key.id(),
                            chatChannelTitle = team_chat_channel.title,
                            userKeyId = player_data_temp.userKeyId,
                            userTitle = player_data_temp.userTitle,
                            userFirebaseUser = player_data_temp.firebaseUser,
                            post_count = 0,
                            chatChannelRefKeyId = match_team.key.id(),
                            channel_type = 'matchteam',
                            #chatChannelOwnerKeyId = authorized_user.key.id()
                        )

                    taskUrl='/task/chat/channel/list_changed'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': player_data_temp.firebaseUser,
                                                                                    'userKeyId': player_data_temp.key.id(),
                                                                                    'textMessage': chat_message
                                                                                    }, countdown = 2)

                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': player_data_temp.firebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })


            ## add the message to the database
            chat_message_copy = "Match found.  Bringing up a server."
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
            matches_created = matches_created +1


        if matches_created:
            match_task_status.successful_runs = match_task_status.successful_runs +1
            match_task_status.successful_match_count = match_task_status.successful_match_count + matches_created
            match_task_status.consecutive_failed_runs = 0

        ## TODO team_fill_incomplete reset

        ## are there any leftovers?  Any more in the batch?
        playersRequiredForEachMatch = game_mode.teams * game_mode.playersPerTeam
        if len_pending_players % playersRequiredForEachMatch > 0:
            logging.info('there are leftover players that could not make it into this matchmaker batch')
            mtsController.update(match_task_status)

            ## send an alert out to discord - if configured
            if match_task_status.discord_subscribe:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "[ %s ] [ %s %s %s ] [ Matches found: %s ] [ In Queue: %s ] Checking again in %s seconds" %(match_task_status.mode, match_task_status.rankMin,
                                                                                                                    match_task_status.rankMedian,
                                                                                                                    match_task_status.rankMax,
                                                                                                                    matches_created, len_pending_players, MATCHMAKER_QUEUE_PROCESS_REQUEUE_LEFTOVER_SECONDS)
                    url = "http://ue4topia.appspot.com/#/game/%s" % match_task_status.gameKeyId
                    discord_data = { "embeds": [{"title": "Matchmaker Status", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(match_task_status.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord push fail')

            ## requeue the task
            taskUrl='/task/game/match/queue/process'
            taskqueue.add(url=taskUrl, queue_name='gameMatchQueueProcess', params={'key_id': match_task_status.key.id()}, countdown = MATCHMAKER_QUEUE_PROCESS_REQUEUE_LEFTOVER_SECONDS,)
            return
        if more:
            logging.info('there are more players waiting in the database that did not get included in this matchmaker batch')
            mtsController.update(match_task_status)

            ## send an alert out to discord - if configured
            if match_task_status.discord_subscribe:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "[ %s ] [ %s %s %s ] [ Matches found: %s ] [ In Queue: %s ] QUEUE FULL! Checking again in %s seconds" %(match_task_status.mode, match_task_status.rankMin,
                                                                                                                    match_task_status.rankMedian,
                                                                                                                    match_task_status.rankMax, matches_created, len_pending_players, MATCHMAKER_QUEUE_PROCESS_REQUEUE_MORE_SECONDS)
                    url = "http://ue4topia.appspot.com/#/game/%s" % match_task_status.gameKeyId
                    discord_data = { "embeds": [{"title": "Matchmaker Status", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(match_task_status.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord push fail')
            ## requeue the task
            taskUrl='/task/game/match/queue/process'
            taskqueue.add(url=taskUrl, queue_name='gameMatchQueueProcess', params={'key_id': match_task_status.key.id()}, countdown = MATCHMAKER_QUEUE_PROCESS_REQUEUE_MORE_SECONDS,)
            return

        ## If this task is failing more than our threshold, kill it.
        if match_task_status.consecutive_failed_runs < MATCHMAKER_QUEUE_PROCESS_MAXIMUM_CONSECUTIVE_FAILURES:
            logging.info('task complete.  no leftover players, but we are still under our threshold.')

            match_task_status.consecutive_failed_runs = match_task_status.consecutive_failed_runs +1
            match_task_status.failed_runs = match_task_status.failed_runs + 1
            mtsController.update(match_task_status)

            ## send an alert out to discord - if configured
            if match_task_status.discord_subscribe:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "[ %s ] [ %s %s %s ] [ Matches found: %s ] [ In Queue: %s ] Queue Empty.  Checking again in %s seconds" %(match_task_status.mode, match_task_status.rankMin,
                                                                                                                    match_task_status.rankMedian,
                                                                                                                    match_task_status.rankMax, matches_created, len_pending_players, MATCHMAKER_QUEUE_PROCESS_REQUEUE_EMPTY_SECONDS)
                    url = "http://ue4topia.appspot.com/#/game/%s" % match_task_status.gameKeyId
                    discord_data = { "embeds": [{"title": "Matchmaker Status", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(match_task_status.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord push fail')

            ##  requeue the task
            taskUrl='/task/game/match/queue/process'
            taskqueue.add(url=taskUrl, queue_name='gameMatchQueueProcess', params={'key_id': match_task_status.key.id()}, countdown = MATCHMAKER_QUEUE_PROCESS_REQUEUE_EMPTY_SECONDS,)
            return
        else:
            logging.info('task complete.  no leftover players, and we have exceeded our threshold.  Terminating.')

            ## send an alert out to discord - if configured
            if match_task_status.discord_subscribe:
                try:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "[ %s ] [ %s %s %s ] [ Matches found: %s ] [ In Queue: %s ] Queue Empty.  Shutting Down." %(match_task_status.mode, match_task_status.rankMin,
                                                                                                                    match_task_status.rankMedian,
                                                                                                                    match_task_status.rankMax, matches_created, len_pending_players)
                    url = "http://ue4topia.appspot.com/#/game/%s" % match_task_status.gameKeyId
                    discord_data = { "embeds": [{"title": "Matchmaker Status", "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(match_task_status.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                except:
                    logging.info('discord push fail')

            ## delete the match_task_status
            mtsController.delete(match_task_status)
            return
