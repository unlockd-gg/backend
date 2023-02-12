import logging
import os
import datetime
import string
import json
from httplib2 import Http
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from oauth2client.client import GoogleCredentials
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.tournament_sponsors import TournamentSponsorsController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.ads import AdsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class InfoHandler(BaseHandler):
    def post(self):
        """
        Send match info
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        Optional POST parameters:  session_host_address, session_id
        """

        matchController = MatchController()
        mpController = MatchPlayersController()
        ucontroller = UsersController()
        tournamentSponsorController = TournamentSponsorsController()
        adController = AdsController()
        gameModeController = GameModesController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        gameController = GamesController()

        try:
            match = matchController.verify_signed_auth(self.request)
        except:
            match = False

        if match == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            ipAddress = os.environ["REMOTE_ADDR"]
            logging.info("ipAddress: %s"% ipAddress)

            game = gameController.get_by_key_id(match.gameKeyId)

            if not game:
                logging.info('game not found')
                return self.render_json_response(
                    authorization = True,
                    error= "The game was not found."
                    )

            dirty = False
            session_host_address = self.request.POST.get('session_host_address', None)
            session_id = self.request.POST.get('session_id', None)
            ## session_host_address is set in task/vm/allocate
            # don't overwrite it here.
            #if match.session_host_address != session_host_address:
            #    match.session_host_address = session_host_address
            #    dirty = True
            if match.session_id != session_id:
                match.session_id = session_id
                dirty = True

            if dirty:
                matchController.update(match)

            ## we want to get the player list, and format it for easy processing UE side.
            match_players = mpController.get_list_by_matchKeyId(match.key.id())

            players = []

            credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
            http_auth = credentials.authorize(Http())
            headers = {"Content-Type": "application/json"}

            for mplayer in match_players:
                logging.info('adding player')
                players.append(mplayer.to_json())

                ## we also want to update the match player here so the next match check will inform them that the process is complete, and they should join.
                mplayer.matchmakerServerReady = True
                mplayer.matchmakerJoinable = True
                mplayer.session_host_address = match.session_host_address
                mplayer.session_id = match.session_id
                mpController.update(mplayer)

                ## Push!


                match_data = {'key_id': mplayer.matchKeyId,
                                'matchmakerStarted': mplayer.matchmakerStarted,
                                'matchmakerPending': mplayer.matchmakerPending,
                                'matchmakerFoundMatch': mplayer.matchmakerFoundMatch,
                                'matchmakerFinished': mplayer.matchmakerFinished,
                                'matchmakerServerReady': mplayer.matchmakerServerReady,
                                'matchmakerJoinable': mplayer.matchmakerJoinable,
                                'session_host_address': match.hostConnectionLink or "",
                                'matchType': match.gameModeTitle,
                                'session_id': match.session_id or ""
                                }

                match_json = json.dumps(match_data)

                ## moving matchmaker complete to a task

                taskUrl='/task/game/match/matchmaker_complete'
                taskqueue.add(url=taskUrl, queue_name='matchmakerPush', params={'firebaseUser': mplayer.firebaseUser,
                                                                                'match_json': match_json
                                                                                }, countdown = 2)


            ## TODO set online in match

            # TODO update firebase
            """
            if not match.invisible:
                logging.info('visible')
                if not match.invisible_developer_setting:
                    logging.info('visible-dev')
                    taskUrl='/task/match/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': match.key.id()}, countdown = 2,)
            """

            ## TODO deal with sponsors
            ## Is this a tournament match?
            ## get the sponsors
            sponsor_textures = []
            if match.tournamentKeyId:
                logging.info('this is a tournament match')
                sponsors = tournamentSponsorController.get_list_by_tournamentKeyId(match.tournamentKeyId)
                for sponsor in sponsors:
                    logging.info('found a sponsor')
                    sponsor_textures.append(sponsor.inGameTextureServingUrl)
            else:
                logging.info('not a tournament match ')

                ## check ads
                ## get the game mode
                game_mode = gameModeController.get_by_key_id(match.gameModeKeyId)
                if game_mode:
                    logging.info('found game_mode')
                    ads_per_match_maximum = game_mode.ads_per_match_maximum

                    potential_ads = adController.get_active_highest_gameModeKeyId(game_mode.key.id(), ads_per_match_maximum)

                    if len(potential_ads) > 0:
                        logging.info('found potential ads')
                        for potential_ad in potential_ads:
                            logging.info('found a potential ad')



                            if potential_ad.currencyBalance > potential_ad.bid_per_impression:
                                logging.info('Ad wallet has enough balance')

                                ## No game transaction here.
                                ## Game transaction is created in the ad process transactions script.
                                sponsor_textures.append(potential_ad.textures)

                                ## set up transaction for the Ad
                                description = "Ad shown"
                                transactionController.create(
                                    amountInt = -potential_ad.bid_per_impression,
                                    ##amount = ndb.FloatProperty(indexed=False) # for display
                                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                                    description = description,
                                    #userKeyId = authorized_user.key.id(),
                                    #firebaseUser = authorized_user.firebaseUser,
                                    ##targetUserKeyId = ndb.IntegerProperty()
                                    adKeyId = potential_ad.key.id(),
                                    adTitle = potential_ad.title,
                                    ##  transactions are batched and processed all at once.
                                    transactionType = "ad",
                                    transactionClass = "impression",
                                    transactionSender = True,
                                    transactionRecipient = False,
                                    #recipientTransactionKeyId = recipient_transaction.key.id(),
                                    submitted = True,
                                    processed = False,
                                    materialIcon = MATERIAL_ICON_AD_SHOWN,
                                    materialDisplayClass = "md-accent"
                                )

                                ## then start tasks to process them

                                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                                pushable = lockController.pushable("ad:%s"%potential_ad.key.id())
                                if pushable:
                                    logging.info('ad pushable')
                                    taskUrl='/task/ad/transaction/process'
                                    taskqueue.add(url=taskUrl, queue_name='adTransactionProcess', params={
                                                                                                            "key_id": potential_ad.key.id()
                                                                                                        }, countdown=2)

                    else:
                        logging.info('no potential ads found.')

                        ## todo check game mode preferences on how to handle this.

                        if game_mode.ads_default_textures:
                            sponsor_textures.append(game_mode.ads_default_textures)


            datetime_iso = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

            return self.render_json_response(
                matchKeyId = str(match.key.id()),
                authorization = True,
                players = players,
                admissionFee = match.admissionFee,
                title = match.title,
                gameModeKeyId = match.gameModeKeyId,
                gameModeTitle = match.gameModeTitle,
                api_version = 1,
                sponsors = sponsor_textures,
                charactersEnabled = game.characters_enabled,
                serverTime = datetime_iso,
                metaMatchTravelUrl = match.metaMatchTravelUrl,
                metaMatchCustom = match.metaMatchCustom,
                region = match.continuous_server_region
            )
