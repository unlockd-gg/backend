import endpoints
import logging
import uuid
import urllib
import json
import google.oauth2.id_token
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote

from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.tournament_sponsors import TournamentSponsorsController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController

from apps.uetopia.providers.compute_engine_zonemap import region_list_ce_readable, region_human_to_ce_readable

from apps.uetopia.models.tournaments import *
from apps.uetopia.models.tournament_sponsors import *
from apps.uetopia.models.match import MatchResponse, MatchCollection


from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="tournaments", version="v1", description="Tournament API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class TournamentApi(remote.Service):
    @endpoints.method(TOURNAMENT_CREATE_RESOURCE, TournamentResponse, path='tournamentCreate', http_method='POST', name='create')
    def tournamentCreate(self, request):
        """ Create a tournament """
        logging.info("tournamentCreate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TournamentResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return TournamentResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TournamentResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gameController = GamesController()
        gameModeController = GameModesController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        tournamentController = TournamentsController()
        tournamentSponsorController = TournamentSponsorsController()
        groupController = GroupsController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGamesController = GroupGamesController()

        if request.gameKeyId:
            game = gameController.get_by_key_id(int(request.gameKeyId))
        else:
            game = gameController.get_by_key_id(int(request.gameKeyIdStr))

        if not game:
            logging.info('no game found')
            return TournamentResponse(response_message='Error: Game not found.')

        ## make sure tournaments are supported.
        if not game.tournaments_allowed:
            logging.info('tournaments are not allowed on this game')
            return TournamentResponse(response_message='Error: Tournaments are not allowed on this game.')

        groupKeyId = request.groupKeyId

        ## defaults
        groupTitle = None
        iconServingUrl = game.icon_url
        bannerServingUrl = None
        cssServingUrl = None
        groupMembersOnly = None
        setup_group_sponsorship = False

        if groupKeyId:
            group = groupController.get_by_key_id(groupKeyId)
            if group:
                ##  make sure the group is connected to this game.
                group_game = groupGamesController.get_by_groupKeyId_gameKeyId(groupKeyId, game.key.id())
                if group_game:

                    ## make sure this user has permissions to create tournaments for the group
                    group_user = groupUserController.get_by_groupKeyId_userKeyId(groupKeyId, authorized_user.key.id())
                    if group_user:
                        ## get permissions for the user
                        group_user_permissions = groupRoleController.get_by_key_id(group_user.roleKeyId)
                        if group_user_permissions:
                            if group_user_permissions.create_tournaments:
                                groupTitle = group.title
                                iconServingUrl = group.iconServingUrl
                                bannerServingUrl = group.bannerServingUrl
                                cssServingUrl = group.cssServingUrl
                                groupMembersOnly = request.groupMembersOnly
                                setup_group_sponsorship = True
                            else:
                                ## TODO send a chat or something
                                logging.info('TODO send a chat or something')



        title = request.title or "Default Server Title"

        ## TODO make sure the player is not already in a tournament

        playerBuyIn = request.playerBuyIn
        additionalPrizeFromHost = request.additionalPrizeFromHost

        ## TODO check these incoming values for sanity
        additionalPrizeFromHost = request.additionalPrizeFromHost
        if additionalPrizeFromHost <0:
            return TournamentResponse(response_message="""Error: Negative contributions are not permitted.""" )


        ## verify that the player has enough non-hold btc to cover it
        if not authorized_user.currencyBalance >= additionalPrizeFromHost:
            return TournamentResponse(response_message="""Error: Your contributiion is greater than your available balance. You can't create this tournament.""" )


        # get the game mode
        if request.gameModeKeyId:
            game_mode = gameModeController.get_by_key_id(int(request.gameModeKeyId))
        else:
            game_mode = gameModeController.get_by_gameKeyId_onlineSubsystemReference(game.key.id(), request.gameMode)

        if not game_mode:
            logging.info('no game mode found')
            return TournamentResponse(response_message='Error: No game mode Found. ', response_successful=False)

        ## make sure the buy in is valid

        ## it should be more than the game_mode admission fee *2
        if playerBuyIn < game_mode.admissionFeePerPlayer * 2:
            error_msg = 'Error:  The player buy-in was too low.  It needs to be more than %s ' % str(game_mode.admissionFeePerPlayer * 2)
            logging.info(error_msg)
            return TournamentResponse(response_message=error_msg, response_successful=False)


        if request.teamMin:
            if TOURNAMENT_MAXIMUM_TEAMS > request.teamMin > 1:
                teamMin = request.teamMin
            else:
                teamMin = 2
        else:
            teamMin = 2
        if request.teamMax:
            if request.teamMax > TOURNAMENT_MAXIMUM_TEAMS:
                teamMax = TOURNAMENT_MAXIMUM_TEAMS
            else:
                teamMax = request.teamMax
        else:
            teamMax = 2

        ## take the additionalPrizeFromHost money out of the player's balance
        description = "Created Tournament Prize: %s for %s" %(request.title, additionalPrizeFromHost)
        transactionController.create(
            amountInt = -additionalPrizeFromHost,
            description = description,
            userKeyId = authorized_user.key.id(),
            firebaseUser = authorized_user.firebaseUser,
            transactionType = "user",
            transactionClass = "tournament_prize",
            transactionSender = True,
            transactionRecipient = False,
            #recipientTransactionKeyId = recipient_transaction.key.id(),
            submitted = True,
            processed = False,
            materialIcon = MATERIAL_ICON_TOURNAMENT,
            materialDisplayClass = "md-accent"


        )
        pushable = lockController.pushable("user:%s"%authorized_user.key.id())
        if pushable:
            logging.info('user pushable')
            taskUrl='/task/user/transaction/process'
            taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                "key_id": authorized_user.key.id()
                                                                            }, countdown=2)

        ## deal with timestamps
        ## TODO make these user selectable so they can plan tournaments in advance

        signupStartTime = datetime.datetime.now()
        signupEndTime = signupStartTime + TOURNAMENT_SIGNUP_DURATION_DEFAULT
        playStartTime = signupEndTime + TOURNAMENT_SIGNUP_TO_PLAY_TRANSITION_DEFAULT
        playEndTime = playStartTime + TOURNAMENT_PLAY_DURATION_DEFAULT

        ## TODO convert the human readable Region into CE readable region

        region = "us-central1"
        if request.region:
            logging.info('found region in request')
            if request.region in region_list_ce_readable:
                logging.info('region is already in the correct format')
                region = request.region
            else:
                region = region_human_to_ce_readable(request.region)

        if request.groupMembersOnly:
            groupMembersOnly = True
        else:
            groupMembersOnly = False

        ## create the tournament
        tournament = tournamentController.create(
            title = request.title,
            description = request.description,

            #platformKey = game.platformKey,
            #platformTitle = game.platformName,

            gameKeyId = game.key.id(),
            gameTitle = game.title,

            ## group stuff
            groupKeyId = groupKeyId,
            groupTitle = groupTitle,
            #iconServingUrl = iconServingUrl,
            #bannerServingUrl = bannerServingUrl,
            #cssServingUrl = cssServingUrl,
            groupMembersOnly = groupMembersOnly,

            hostUserKeyId = authorized_user.key.id(),
            hostUserTitle = authorized_user.title,

            signupStartTime = signupStartTime,
            signupEndTime = signupEndTime,

            playStartTime = playStartTime,
            playEndTime = playEndTime,

            gameModeKeyId = game_mode.key.id(),
            gameModeTitle = game_mode.onlineSubsystemReference,

            teamMin = teamMin,
            teamMax = teamMax,

            region = region,

            playerBuyIn = request.playerBuyIn,
            additionalPrizeFromHost = request.additionalPrizeFromHost,
            prizeDistributionType = "Winner Takes All",
            #estimatedTotalWinnings = request.additionalPrizeFromHost,
            currencyBalance = request.additionalPrizeFromHost,

            ## State flags
            initialized = True,  ## TODO remove the hardcoding so starttime can work
            signupsStarted = True, ## TODO remove the hardcoding so starttime can work
            signupsFinished = False,
            playStarted = False,
            playFinished = False,
            completed = False,
            finalized = False
        )

        ## Make tournament chat channel

        ## create the chat channel for this group
        tournament_chat_title = request.title + " chat"
        chat_channel = ChatChannelsController().create(
            title = tournament_chat_title,
            #text_enabled = True,
            #data_enabled = False,
            channel_type = 'tournament',
            adminUserKeyId = authorized_user.key.id(),
            refKeyId = tournament.key.id(),
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
            chatChannelRefKeyId = tournament.key.id(),
            channel_type = 'tournament',
            chatChannelOwnerKeyId = authorized_user.key.id()
        )

        if setup_group_sponsorship:
            ## this is a group tournemant.  By defualt the creating group is automatically listed as a sponsor.
            tournamentSponsorController.create(
                title = "Host",
                description = "Tournament Host",

                tournamentKeyId = tournament.key.id(),
                tournamentTitle = tournament.title,

                gameKeyId = tournament.gameKeyId,
                gameTitle = tournament.gameTitle,

                groupKeyId = group.key.id(),
                groupTitle = group.title,
                groupIconUrl = group.iconServingUrl,

                hostUserKeyId = authorized_user.key.id(),
                hostUserTitle = authorized_user.title,

                inGameTextureServingUrl = group_game.inGameTextureServingUrl
            )

        chat_message = "> Tournament %s created" % request.title

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

        ## Send the creator a tournament list changed notification
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}
        entity_json = json.dumps({'message':chat_message})
        # ignore if it's failing
        try:
            URL = "%s/user/%s/tournaments/list_changed" % (HEROKU_SOCKETIO_SERVER, authorized_user.firebaseUser)
            resp, content = http_auth.request(URL,
                                ##"PATCH",
                              "PUT", ## Write or replace data to a defined path,
                              entity_json,
                              headers=headers)

            logging.info(resp)
            logging.info(content)
        except:
            logging.error('heroku error')


        ## send everyone the new active list
        taskUrl='/task/tournament/push'
        taskqueue.add(url=taskUrl, queue_name='tournamentPush', params={'key_id': tournament.key.id()}, countdown = 2,)

        ## TODO timer chat task

        ## task to watch after the tournament

        ## auto create a group event

        ## Sense
        """
        SenseController().create(
            target_type = 'Player',
            target_key = player.key.urlsafe(),
            target_title = player.title,
            ref_type = 'Tournament',
            ref_key = tournament.key.urlsafe(),
            action = 'Tournament Created',
            title = '%s Created Tournament %s' % (player.title, tournament.title),
            description = '%s Created Tournament %s' % (player.title, tournament.title),
            ##amount = request.amount
        )
        """

        ## do slack/discord pushes for the game if enabled
        if game.slack_subscribe_new_tournaments and game.slack_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
            message = "New Tournament: %s | %s" % (link, tournament.title)
            slack_data = {'text': message}
            data=json.dumps(slack_data)
            resp, content = http_auth.request(game.slack_webhook,
                              "POST",
                              data,
                              headers=headers)

        if game.discord_subscribe_new_tournaments and game.discord_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
            message = "%s  %s" % (tournament.title, link)
            #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
            discord_data = { "embeds": [{"title": "New Tournament", "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook,
                              "POST",
                              data,
                              headers=headers)

        ## do discord pushes for the group
        if groupKeyId:
            if group:
                if group.discord_subscribe_tournaments and group.discord_webhook:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
                    message = "%s  %s" % (tournament.title, link)
                    #url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                    discord_data = { "embeds": [{"title": "New Tournament", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(group.discord_webhook,
                                      "POST",
                                      data,
                                      headers=headers)
                if group.slack_subscribe_tournaments:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    link = "https://ue4topia.appspot.com/#/game/%s/tournament/%s" % (tournament.gameKeyId, tournament.key.id())
                    message = "New Tournament: %s | %s" % (link, tournament.title)
                    slack_data = {'text': message}
                    data=json.dumps(slack_data)
                    resp, content = http_auth.request(group.slack_webhook,
                                      "POST",
                                      data,
                                      headers=headers)



        ## send the tournament data back
        return TournamentResponse(key_id = tournament.key.id(),
            title = tournament.title,
            description = tournament.description,

            gameKeyId = tournament.gameKeyId,
            gameModeKeyId = tournament.gameModeKeyId,
            groupKeyId = tournament.groupKeyId,

            #teamSize = tournament.teamSize,
            teamMin = tournament.teamMin,
            teamMax = tournament.teamMax,

            completed = tournament.completed,
            finalized = tournament.finalized,
            resultDisplayText = tournament.resultDisplayText,

            playerBuyIn = tournament.playerBuyIn,
            additionalPrizeFromHost = tournament.additionalPrizeFromHost,

            groupMembersOnly =tournament.groupMembersOnly,
            prizeDistributionType = tournament.prizeDistributionType,
            response_message="""Success.  Tournament Created.""",
            response_successful=True )

    @endpoints.method(TOURNAMENT_GET_RESOURCE, TournamentResponse, path='tournamentGet', http_method='POST', name='tournament.get')
    def tournamentGet(self, request):
        """ Get a tournament """
        logging.info("tournamentGet")
        tournamentController = TournamentsController()
        tournamentSponsorController = TournamentSponsorsController()
        matchController = MatchController()
        teamController = TeamsController()

        logging.info(request.key_id)
        logging.info(request.keyIdStr)

        try:

            tournament = tournamentController.get_by_key_id(request.key_id)
        except:
            logging.info('No tournament found with key_id - attempting keyIdStr')
            try:

                tournament = tournamentController.get_by_key_id(int(request.keyIdStr))
            except:
                logging.error('No tournament could be found by key_id or keyIdStr')
                return TournamentResponse(
                        key_id = None,
                        response_message = 'No tournament could be found with the supplied key'
                        )


        if tournament:

            teams_json = []

            teams = teamController.get_list_by_tournament(tournament.key.id())

            for team in teams:
                teams_json.append(TeamResponse(
                    key_id = team.key.id(),
                    title = team.title,
                    teamSizeMax = team.teamSizeMax,
                    teamSizeCurrent = team.teamSizeCurrent,
                    teamFull = team.teamFull,
                    initialized = team.initialized,
                    recruiting = team.recruiting,
                    inTournament = team.inTournament,
                    inMatch = team.inMatch,
                )
                )

            ## sponsors
            sponsors_out = []
            sponsors = tournamentSponsorController.get_list_by_tournamentKeyId(tournament.key.id())
            for sponsor in sponsors:
                sponsors_out.append(TournamentSponsorResponse(
                    title = sponsor.title,
                    description = sponsor.description,
                    gameKeyId = sponsor.gameKeyId,
                    groupKeyId = sponsor.groupKeyId,
                    groupIconUrl = sponsor.groupIconUrl
                ))

            ## matches
            tiers = []
            if not tournament.total_rounds:
                tournament.total_rounds = 0

            for thistier in range(tournament.total_rounds ):
                index =thistier+1
                logging.info("grabbing matches for round: %s" %index)

                matches_json = []

                matches = matchController.get_matches_by_tournamentKeyId_tournamentTier(tournament.key.id(), index)
                for match in matches:
                    logging.info('found match in this round')
                    if match.tournamentMatchWinnerKeyId == match.tournamentTeamKeyId1:
                        TournamentTeam1Winner = True
                        TournamentTeam1Loser = False
                        TournamentTeam2Winner = False
                        TournamentTeam2Loser = True
                    elif match.tournamentMatchWinnerKeyId == match.tournamentTeamKeyId2:
                        TournamentTeam1Winner = False
                        TournamentTeam1Loser = True
                        TournamentTeam2Winner = True
                        TournamentTeam2Loser = False
                    else:
                        TournamentTeam1Winner = False
                        TournamentTeam1Loser = False
                        TournamentTeam2Winner = False
                        TournamentTeam2Loser = False

                    matches_json.append(MatchResponse(
                        key_id = match.key.id(),
                        title = match.title,
                        #description = match.description,
                        allPlayersJoined = match.allPlayersJoined,
                        allPlayersCommitted = match.allPlayersCommitted,
                        allPlayersApproved = match.allPlayersApproved,
                        allPlayersLeft = match.allPlayersLeft,
                        allPlayersVerified = match.allPlayersVerified,
                        allPlayersReportedFailure = match.allPlayersReportedFailure,
                        #gameJoinLink = match.gameJoinLink,
                        #wagerPerPlayerSatoshi = match.wagerPerPlayerSatoshi,
                        #playerMin = match.playerMin,
                        #playerMax = match.playerMax,
                        #password = match.password,
                        #playersCurrent = match.playersCurrent,
                        tournamentTeamTitle1 = match.tournamentTeamTitle1,
                        tournamentTeamTitle2 = match.tournamentTeamTitle2,
                        tournamentTeamKeyId1 = str(match.tournamentTeamKeyId1),
                        tournamentTeamKeyId2 = str(match.tournamentTeamKeyId2),
                        TournamentTeam1Winner = TournamentTeam1Winner,
                        TournamentTeam1Loser = TournamentTeam1Loser,
                        TournamentTeam2Winner = TournamentTeam2Winner,
                        TournamentTeam2Loser = TournamentTeam2Loser,
                        )
                )

                tiers.append(MatchCollection(matches=matches_json, tier=index))


            return TournamentResponse(
                    key_id = tournament.key.id(),
                    keyIdStr = str(tournament.key.id()),
                    title = tournament.title,
                    description = tournament.description,
                    region = tournament.region,
                    #teamSize = tournament.teamSize,
                    teamMin = tournament.teamMin,
                    teamMax = tournament.teamMax,

                    playerBuyIn = tournament.playerBuyIn,
                    additionalPrizeFromHost = tournament.additionalPrizeFromHost,

                    completed = tournament.completed,
                    finalized = tournament.finalized,
                    resultDisplayText = tournament.resultDisplayText,

                    groupMembersOnly = tournament.groupMembersOnly,
                    prizeDistributionType = tournament.prizeDistributionType,
                    gameModeTitle = tournament.gameModeTitle,

                    signupsStarted = tournament.signupsStarted,
                    signupsFinished = tournament.signupsFinished,
                    playStarted = tournament.playStarted,
                    playFinished = tournament.playFinished,

                    teams = teams_json,
                    tiers = tiers,
                    sponsors = sponsors_out
                )
        else:
            return TournamentResponse(
                    key_id = None
                    )

    @endpoints.method(TOURNAMENT_GET_RESOURCE, TournamentCollection, path='tournamentCollectionGet', http_method='POST', name='tournament.collection.get')
    def tournamentCollectionGet(self, request):
        """ Get a collection of tournaments """
        logging.info("tournamentCollectionGet")

        usersController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TournamentCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return TournamentResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = usersController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TournamentResponse(response_message='Error: No User Record Found. ', response_successful=False)


        tournamentController = TournamentsController()
        groupUserController = GroupUsersController()

        tournaments = tournamentController.get_public_not_completed_by_gameKeyId(int(request.gameKeyIdStr))

        response_list = []

        for tournament in tournaments:
            response_list.append(TournamentResponse(
                    key_id = tournament.key.id(),
                    keyIdStr = str(tournament.key.id()),
                    title = tournament.title,
                    description = tournament.description,
                    #teamSize = tournament.teamSize,
                    teamMin = tournament.teamMin,
                    teamMax = tournament.teamMax,

                    playerBuyIn = tournament.playerBuyIn,
                    additionalPrizeFromHost = tournament.additionalPrizeFromHost,

                    completed = tournament.completed,
                    finalized = tournament.finalized,
                    resultDisplayText = tournament.resultDisplayText,

                    groupMembersOnly = tournament.groupMembersOnly,
                    groupTitle = tournament.groupTitle,
                    prizeDistributionType = tournament.prizeDistributionType,

                    signupsStarted = tournament.signupsStarted,
                    signupsFinished = tournament.signupsFinished,
                    playStarted = tournament.playStarted,
                    playFinished = tournament.playFinished,

                    #teams = teams_json,
                    #tiers = tiers
                )

            )
        logging.info('found %s public tournaments' % len(tournaments))

        ## get group members for this user so that we can get group tournaments

        group_users = groupUserController.get_list_by_userKeyId(authorized_user.key.id())
        if len(group_users) > 0:
            logging.info('found group membership(s) - checking for group tournaments')
            for group_user in group_users:
                group_tournaments = tournamentController.get_group_not_completed_by_gameKeyId(int(request.gameKeyIdStr), group_user.groupKeyId)
                for g_tournament in group_tournaments:
                    logging.info('Found a group tournament')
                    response_list.append(TournamentResponse(
                            key_id = g_tournament.key.id(),
                            title = g_tournament.title,
                            description = g_tournament.description,
                            #teamSize = tournament.teamSize,
                            teamMin = g_tournament.teamMin,
                            teamMax = g_tournament.teamMax,

                            playerBuyIn = g_tournament.playerBuyIn,
                            additionalPrizeFromHost = g_tournament.additionalPrizeFromHost,

                            completed = g_tournament.completed,
                            finalized = g_tournament.finalized,
                            resultDisplayText = g_tournament.resultDisplayText,

                            groupMembersOnly = g_tournament.groupMembersOnly,
                            groupTitle = g_tournament.groupTitle,
                            prizeDistributionType = g_tournament.prizeDistributionType,

                            signupsStarted = g_tournament.signupsStarted,
                            signupsFinished = g_tournament.signupsFinished,
                            playStarted = g_tournament.playStarted,
                            playFinished = g_tournament.playFinished,

                            #teams = teams_json,
                            #tiers = tiers
                        )

                    )




        return TournamentCollection(
            tournaments = response_list,
            response_message = "Success.",
            response_successful = True
        )

    @endpoints.method(TOURNAMENT_GET_RESOURCE, TournamentResponse, path='tournamentJoin', http_method='POST', name='tournament.join')
    def tournamentJoin(self, request):
        """ Join a tournament """
        logging.info("tournamentJoin")

        usersController = UsersController()

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TournamentResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return TournamentResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = usersController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TournamentResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gameController = GamesController()
        gameModeController = GameModesController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        tournamentController = TournamentsController()

        teamController = TeamsController()
        teamMembersController = TeamMembersController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        if request.key_id:
            tournament = tournamentController.get_by_key_id(request.key_id)
        else:
            tournament = tournamentController.get_by_key_id(int(request.keyIdStr))

        if not tournament:
            logging.info('tournament not found')
            return TournamentResponse(response_message='Error: No Tournament Found. ', response_successful=False)

        # check balance
        if authorized_user.currencyBalance < tournament.playerBuyIn:
            return TournamentResponse(response_message="""Error: The tournament's buy-in is greater than your available balance. You can't join""", response_successful=False )

        game_mode = gameModeController.get_by_key_id(tournament.gameModeKeyId)
        if not game_mode:
            logging.info('game_mode not found')
            return TournamentResponse(response_message='Error: No game_mode Found. ', response_successful=False)

        ## make sure there is space in the tournament for this team to join
        teams = teamController.get_list_by_tournament(tournament.key.id())
        if len(teams) >= tournament.teamMax:
            logging.info('tournament full')
            return TournamentResponse(response_message='Error: Tournament full. ', response_successful=False)



        ## get the existing team member in this tournament
        team_member_in_this_tournament = teamMembersController.get_by_nextTournamentKeyId_userKeyId(tournament.key.id(), authorized_user.key.id())
        if team_member_in_this_tournament:
            logging.info('Already joined.')
            return TournamentResponse(response_message='Error: Already joined this tournament. ', response_successful=False)

        ## get any team this user is a member of
        team_member_in_this_game = teamMembersController.get_by_gameKeyId_userKeyId(tournament.gameKeyId, authorized_user.key.id())

        if team_member_in_this_game:
            logging.info('this user is a member of a team')
            if not team_member_in_this_game.captain:
                logging.info('Not team captain.')
                return TournamentResponse(response_message='Error: Only the team captain can join a tournament. ', response_successful=False)

            ## make sure this player is not in a tournament already
            ## get the team
            team = teamController.get_by_key_id(team_member_in_this_game.teamKeyId)
            if team.inTournament:
                logging.info('Player already in a tournament')
                return TeamResponse(response_message="Error: You are already in a tournament.  ", response_successful=False)



        ## TODO any other checks?



        ## check team size
        if game_mode.playersPerTeam == 1:
            ## It's just a one player tournament.  Create the team if it does not exist, and join the player
            if not team_member_in_this_game:
                logging.info('no team found.  Creating one')
                team = teamController.create(
                    title = authorized_user.title,
                    #description = request.description,
                    pug = False,
                    #teamAvatarTheme = player.avatar_theme,

                    gameKeyId = tournament.gameKeyId,
                    gameTitle = tournament.gameTitle,

                    captainPlayerKeyId = authorized_user.key.id(),
                    captainPlayerTitle = authorized_user.title,

                    nextPlayStartTime = tournament.playStartTime,
                    nextPlayEndTime = tournament.playEndTime,

                    nextTournamentStartTime = tournament.playStartTime,
                    nextTournamentEndTime = tournament.playEndTime,
                    nextTournamentKeyId = tournament.key.id(),
                    nextTournamentTitle = tournament.title,
                    nextTournamentEliminated = False,

                    teamSizeMax = game_mode.playersPerTeam,
                    teamSizeCurrent = 1,
                    teamFull = True,

                    ## State flags
                    initialized = False,
                    recruiting = False,
                    inTournament = True,
                    activeInTournament = False,
                    inMatch = False,
                    purged = False,
                )

                ## Add the captain team player record

                team_member= teamMembersController.create(
                    teamKeyId = team.key.id(),
                    teamTitle = team.title,
                    userKeyId = authorized_user.key.id(),
                    userTitle = authorized_user.title,
                    userFirebaseUser = authorized_user.firebaseUser,
                    gameKeyId = tournament.gameKeyId,
                    gameTitle = tournament.gameTitle,

                    invited = False,
                    joined = True, ## TODO double check that the user should join upon create
                    applicant = False,
                    approved = True,
                    captain = True,
                    denied = False,

                    order = 1,

                    nextTournamentKeyId = tournament.key.id(),
                    nextTournamentTitle = tournament.title,
                )

                ## push team changed
                taskUrl='/task/team/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': team.key.id()}, countdown = 2,)

            else:
                logging.info('found an existing team')
                if not team:
                    team = teamController.get_by_key_id(team_member_in_this_game.teamKeyId)

                team.inTournament = True

                team.nextPlayStartTime = tournament.playStartTime
                team.nextPlayEndTime = tournament.playEndTime

                team.nextTournamentStartTime = tournament.playStartTime
                team.nextTournamentEndTime = tournament.playEndTime
                team.nextTournamentKeyId = tournament.key.id()
                team.nextTournamentTitle = tournament.title
                team.nextTournamentEliminated = False

                teamController.update(team)

                team_member = team_member_in_this_game

            ## Ok we've got a team and team member and we need to subscribe the user to the channels and such.
            all_team_members = []
            all_team_members.append(team_member)

        else:
            ## if it's more than one player, makse sure the team matches the number of players

            if not team_member_in_this_game:
                logging.info('No team.')
                return TournamentResponse(response_message='Error: Form your team before joining a tournament.', response_successful=False)

            ## get all of the team members
            all_team_members = teamMembersController.get_by_teamKeyId(team_member_in_this_game.teamKeyId)

            ## check size
            if len(all_team_members) != game_mode.playersPerTeam:
                logging.info('Wrong number of team members.')
                return TournamentResponse(response_message='Error: Wrong number of team members.', response_successful=False)

            ## check team member balance
            for team_member in all_team_members:
                ## get the user account
                team_member_user = usersController.get_by_key_id(team_member.userKeyId)
                if not team_member_user:
                    logging.error('user account for team member not found')
                    return TournamentResponse(response_message='Error: User account not found for one of your team members', response_successful=False)

                if team_member_user.currencyBalance < tournament.playerBuyIn:
                    return TournamentResponse(response_message="""Error: One of your team members does not have enough CRED to buy-in.  You can't join""", response_successful=False )


            if not team:
                team = teamController.get_by_key_id(team_member_in_this_game.teamKeyId)

            ## update the team flags
            team.recruiting = True
            team.teamFull = False
            team.inTournament = True

            team.nextPlayStartTime = tournament.playStartTime
            team.nextPlayEndTime = tournament.playEndTime

            team.nextTournamentStartTime = tournament.playStartTime
            team.nextTournamentEndTime = tournament.playEndTime
            team.nextTournamentKeyId = tournament.key.id()
            team.nextTournamentTitle = tournament.title
            team.nextTournamentEliminated = False

            teamController.update(team)

            ## we also need to update the team member here
            for team_member in all_team_members:
                team_member.nextTournamentKeyId = tournament.key.id()
                team_member.nextTournamentTitle = tournament.title
                teamMembersController.update(team_member)


        ## now we've got a list of team members
        ## subscribe them all to the tournament chat

        ## get the tournament chat
        chat_channel = chatChannelController.get_by_channel_type_refKeyId('tournament', tournament.key.id())

        for team_member in all_team_members:
            ## Subscribe the player to the tourament chat

            ## first check to see if they are already subscribed.  They may have created the tournament.
            existing_channel_subscription = chatChannelSubscribersController.get_by_channel_and_user(chat_channel.key.id(), team_member.userKeyId)

            if not existing_channel_subscription:
                subscriber = chatChannelSubscribersController.create(
                    online = True,
                    chatChannelKeyId = chat_channel.key.id(),
                    chatChannelTitle = chat_channel.title,
                    userKeyId = team_member.userKeyId,
                    userTitle = team_member.userTitle,
                    userFirebaseUser = team_member.userFirebaseUser,
                    post_count = 0,
                    chatChannelRefKeyId = tournament.key.id(),
                    channel_type = 'tournament',
                    #chatChannelOwnerKeyId = authorized_user.key.id()
                )

                ## Send the chat channel list
                taskUrl='/task/chat/channel/list_changed'
                taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': team_member.userFirebaseUser,
                                                                                'userKeyId': team_member.userKeyId,
                                                                                'textMessage': 'chat channels changed'
                                                                                }, countdown = 2)


        chat_message = "%s joined the tournament" % team.title

        chat_message_record = ChatMessagesController().create(
            chatChannelKeyId = chat_channel.key.id(),
            chatChannelTitle = chat_channel.title,
            #userKeyId = authorized_user.key.id(),
            #userTitle = authorized_user.title,
            text = chat_message,
            #pulled = False
        )

        taskUrl='/task/chat/channel/send'
        taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': chat_channel.key.id(),
                                                                            "message": chat_message,
                                                                            #"userKeyId": authorized_user.key.id(),
                                                                            #"userTitle": authorized_user.title,
                                                                            "chatMessageKeyId": chat_message_record.key.id(),
                                                                            "chatChannelTitle": chat_channel.title,
                                                                            "chatChannelRefType":chat_channel.channel_type,
                                                                            "created":chat_message_record.created.isoformat()
                                                                        }, countdown=2)

        ## check to see if signups can be closed out.
        ## putting this behind a memcache check becuase it's possible for multiple users to submit simultaneously
        pushable = lockController.pushable("tournament-join-finish-signups:%s"%tournament.key.id(), seconds=2)
        if pushable:
            taskUrl='/task/tournament/finish_signups'
            taskqueue.add(url=taskUrl, queue_name='tournamentProcessing', params={'key_id': tournament.key.id()}, countdown=2)

        ## don't push the tournament here.  it happens in finish signups already
        return TournamentResponse(response_message="""Success. Joined""", response_successful=True )

    @endpoints.method(TOURNAMENT_SPONSOR_CREATE_RESOURCE, TournamentSponsorResponse, path='tournamentSponsorCreate', http_method='POST', name='sponsor.create')
    def tournamentSponsorCreate(self, request):
        """ Create a tournament sponsor """
        logging.info("tournamentSponsorCreate")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TournamentSponsorResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return TournamentSponsorResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TournamentSponsorResponse(response_message='Error: No User Record Found. ', response_successful=False)

        tournamentController = TournamentsController()
        tournamentSponsorController = TournamentSponsorsController()
        groupController = GroupsController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGamesController = GroupGamesController()

        ## get the tournament
        tournament = tournamentController.get_by_key_id(request.tournamentKeyId)
        if not tournament:
            logging.info('no tournament found')
            return TournamentSponsorResponse(response_message='Error: No Tournament Found. ', response_successful=False)

        ## get the group being added as sponsor - BY TAG
        group = groupController.get_by_tag(request.groupTag)
        if not group:
            logging.info('no group found')
            return TournamentSponsorResponse(response_message='Error: No Group Found. ', response_successful=False)

        ## make sure it has not been added already
        existing_tournament_sponsor = tournamentSponsorController.get_by_tournamentKeyId_groupKeyId(tournament.key.id(), group.key.id())
        if existing_tournament_sponsor:
            logging.info('existing_tournament_sponsor found')
            return TournamentSponsorResponse(response_message='Error: Already listed as a sponsor. ', response_successful=False)

        ## make sure the group is connected to this game
        group_game = groupGamesController.get_by_groupKeyId_gameKeyId(group.key.id(), tournament.gameKeyId)
        if not group_game:
            logging.info('Group game not found')
            return TournamentSponsorResponse(response_message='Error: Group game not found ', response_successful=False)


        ## the the group member and make sure the role has add_sponsor permission
        group_user = groupUserController.get_by_groupKeyId_userKeyId(group.key.id(), authorized_user.key.id())
        if group_user:
            group_user_permissions = groupRoleController.get_by_key_id(group_user.roleKeyId)
            if group_user_permissions:
                if group_user_permissions.sponsor_tournaments:
                    logging.info('All checks passed - adding sponsor')

                    tournamentSponsorController.create(
                        title = "Host",
                        description = "Tournament Host",

                        tournamentKeyId = tournament.key.id(),
                        tournamentTitle = tournament.title,

                        gameKeyId = tournament.gameKeyId,
                        gameTitle = tournament.gameTitle,

                        groupKeyId = group.key.id(),
                        groupTitle = group.title,
                        groupIconUrl = group.iconServingUrl,

                        hostUserKeyId = authorized_user.key.id(),
                        hostUserTitle = authorized_user.title,

                        inGameTextureServingUrl = group_game.inGameTextureServingUrl
                    )

                    ## update the tournament
                    ## send everyone the new active list
                    taskUrl='/task/tournament/push'
                    taskqueue.add(url=taskUrl, queue_name='tournamentPush', params={'key_id': tournament.key.id()}, countdown = 2,)

                    return TournamentSponsorResponse(key_id = tournament.key.id(),
                        response_message="""Success.  Tournament Sponsor Created.""",
                        response_successful=True )
                else:
                    logging.info('User does not have the sponsor tournaments permission.')
                    return TournamentSponsorResponse(response_message='Error: you do not have the sponsor tournaments permission ', response_successful=False)
            else:
                logging.info('No permissions found')
                return TournamentSponsorResponse(response_message='Error: You do not have permission to add this sponsor', response_successful=False)
        else:
            logging.info('No group user')
            return TournamentSponsorResponse(response_message='Error: You must be a member of the group, and have the sponsor tournaments permission in order to do this.', response_successful=False)

    @endpoints.method(TOURNAMENT_SPONSOR_CREATE_RESOURCE, TournamentSponsorResponse, path='tournamentSponsorDelete', http_method='POST', name='sponsor.delete')
    def tournamentSponsorDelete(self, request):
        """ Delete a tournament sponsor """
        logging.info("tournamentSponsorDelete")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return TournamentSponsorResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return TournamentSponsorResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return TournamentSponsorResponse(response_message='Error: No User Record Found. ', response_successful=False)

        tournamentController = TournamentsController()
        tournamentSponsorController = TournamentSponsorsController()
        groupController = GroupsController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGamesController = GroupGamesController()

        ## get the tournament
        tournament = tournamentController.get_by_key_id(request.tournamentKeyId)
        if not tournament:
            logging.info('no tournament found')
            return TournamentSponsorResponse(response_message='Error: No Tournament Found. ', response_successful=False)

        ## get the group being removed as sponsor
        group = groupController.get_by_key_id(request.groupKeyId)
        if not group:
            logging.info('no group found')
            return TournamentSponsorResponse(response_message='Error: No Group Found. ', response_successful=False)

        ## make sure it has been added already
        existing_tournament_sponsor = tournamentSponsorController.get_by_tournamentKeyId_groupKeyId(tournament.key.id(), group.key.id())
        if not existing_tournament_sponsor:
            logging.info('no existing_tournament_sponsor found')
            return TournamentSponsorResponse(response_message='Error: Not listed as a sponsor. ', response_successful=False)


        ## the the group member and make sure the role has add_sponsor permission
        group_user = groupUserController.get_by_groupKeyId_userKeyId(group.key.id(), authorized_user.key.id())
        if group_user:
            group_user_permissions = groupRoleController.get_by_key_id(group_user.roleKeyId)
            if group_user_permissions:
                if group_user_permissions.sponsor_tournaments:
                    logging.info('All checks passed - deleting sponsor')


                    ## remove it from firebase
                    credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                    http_auth = credentials.authorize(Http())

                    base_tournament_json = json.dumps(tournament.to_json())
                    SPONSORURL = "https://ue4topia.firebaseio.com/groups/%s/tournaments/%s.json" % (existing_tournament_sponsor.groupKeyId, tournament.key.id())

                    resp, content = http_auth.request(SPONSORURL,
                                      "DELETE", ## delete it.
                                      base_tournament_json,
                                      headers=headers)

                    tournamentSponsorController.delete(existing_tournament_sponsor)

                    return TournamentResponse(key_id = tournament.key.id(),
                        response_message="""Success.  Tournament Sponsor Deleted.""",
                        response_successful=True )
                else:
                    logging.info('User does not have the sponsor tournaments permission.')
                    return TournamentSponsorResponse(response_message='Error: you do not have the sponsor tournaments permission ', response_successful=False)
            else:
                logging.info('No permissions found')
                return TournamentSponsorResponse(response_message='Error: You do not have permission to add this sponsor', response_successful=False)
        else:
            logging.info('No group user')
            return TournamentSponsorResponse(response_message='Error: You must be a member of the group, and have the sponsor tournaments permission in order to do this.', response_successful=False)
