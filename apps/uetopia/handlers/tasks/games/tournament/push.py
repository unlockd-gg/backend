import endpoints
import logging
import uuid
import urllib
import json
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

from apps.handlers import BaseHandler

#from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController

from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.tournament_sponsors import TournamentSponsorsController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.teams import TeamsController

from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class TournamentPushHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] TournamentPushHandler")

        ## this is a game key
        key_id = self.request.get('key_id')

        tournament = TournamentsController().get_by_key_id(int(key_id))
        if not tournament:
            logging.error('Tournament not found')
            return

        matchController = MatchController()
        teamController = TeamsController()
        tournamentSponsorController = TournamentSponsorsController()

        ## get teams
        teams = teamController.get_list_by_tournament(int(key_id))

        teams_json = []
        for team in teams:
            teams_json.append(team.to_json())

        tournament.teams = teams_json

        ## get the tiers
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
                    match.TournamentTeam1Winner = True
                    match.TournamentTeam1Loser = False
                    match.TournamentTeam2Winner = False
                    match.TournamentTeam2Loser = True
                elif match.tournamentMatchWinnerKeyId == match.tournamentTeamKeyId2:
                    match.TournamentTeam1Winner = False
                    match.TournamentTeam1Loser = True
                    match.TournamentTeam2Winner = True
                    match.TournamentTeam2Loser = False
                else:
                    match.TournamentTeam1Winner = False
                    match.TournamentTeam1Loser = False
                    match.TournamentTeam2Winner = False
                    match.TournamentTeam2Loser = False

                matches_json.append(match.to_json_tournament_view())

            tiers.append( {u'matches': matches_json,
                            u'tier': index
                            } )

        tournament.tiers = tiers

        ## get sponsors
        sponsors_json = []
        sponsors = tournamentSponsorController.get_list_by_tournamentKeyId(tournament.key.id())
        for sponsor in sponsors:
            sponsors_json.append(sponsor.to_json())

        tournament.sponsors = sponsors_json

        ## push user data to firebase.  overwrite.
        # works on localhost, but not live.
        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        tournament_json = json.dumps(tournament.to_json_with_teams_tiers_and_sponsors())

        if tournament.groupKeyId:
            base_tournament_json = json.dumps(tournament.to_json())
            GROUPURL = "https://ue4topia.firebaseio.com/groups/%s/tournaments/%s.json" % (tournament.groupKeyId, tournament.key.id())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/games/%s/tournaments/%s.json" % (tournament.gameKeyId, tournament.key.id())

        if tournament.finalized:
            logging.info('finalized - removing from firebase')
            resp, content = http_auth.request(URL,
                              "DELETE", ## delete it.
                              tournament_json,
                              headers=headers)
            ##
            if tournament.groupKeyId:
                logging.info('also removing from the group')
                resp, content = http_auth.request(GROUPURL,
                                  "DELETE", ## delete it.
                                  base_tournament_json,
                                  headers=headers)

            ## also update sponsors
            for sponsor in sponsors:
                logging.info('also removing from this sponsor')
                SPONSORURL = "https://ue4topia.firebaseio.com/groups/%s/tournaments/%s.json" % (sponsor.groupKeyId, tournament.key.id())
                resp, content = http_auth.request(SPONSORURL,
                                  "DELETE", ## delete it.
                                  base_tournament_json,
                                  headers=headers)



        else:
            logging.info('updating firebase')
            resp, content = http_auth.request(URL,
                              "PATCH", ## We can update specific children at a location without overwriting existing data using a PATCH request.
                              ## Named children in the data being written with PATCH will be overwritten, but omitted children will not be deleted.
                              tournament_json,
                              headers=headers)

            ##
            if tournament.groupKeyId:
                logging.info('also updating the group')
                resp, content = http_auth.request(GROUPURL,
                                  "PATCH",
                                  base_tournament_json,
                                  headers=headers)

            ## also update sponsors
            for sponsor in sponsors:
                logging.info('also updating this sponsor')
                SPONSORURL = "https://ue4topia.firebaseio.com/groups/%s/tournaments/%s.json" % (sponsor.groupKeyId, tournament.key.id())
                resp, content = http_auth.request(SPONSORURL,
                                  "PATCH", ## delete it.
                                  base_tournament_json,
                                  headers=headers)

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}


        ## get tournament chat channel
        tournament_chat = ChatChannelsController().get_by_channel_type_refKeyId("tournament", tournament.key.id())
        if tournament_chat:
            ## Get tournament subscribers
            tournament_subscribers = ChatChannelSubscribersController().get_by_chatChannelKeyId(tournament_chat.key.id())

            for tournament_subscriber in tournament_subscribers:
                # push out to in-game clients via heroku
                # ignore if it's failing
                try:
                    URL = "%s/%s/tournament/%s" % (HEROKU_SOCKETIO_SERVER, tournament_subscriber.userFirebaseUser, tournament.key.id())
                    resp, content = http_auth.request(URL,
                                        ##"PATCH",
                                      "PUT", ## Write or replace data to a defined path,
                                      tournament_json,
                                      headers=headers)

                    logging.info(resp)
                    logging.info(content)
                except:
                    logging.error('heroku error')




        return
