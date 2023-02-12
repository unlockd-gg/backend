import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.match_task_status import MatchTaskStatusController

from configuration import *

class MatchmakerCheckHandler(BaseHandler):
    def post(self, gameKeyId):
        """
        Cancel Matchmaking for a game
        Requires http headers:  -
        Requires POST parameters:  - userid, matchtype
        """

        ## check this userid
        ## get the game player
        ## are there any existing matches

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        if 'userid' in jsonobject:
            logging.info("Found userid in json")
            userid = int(jsonobject['userid'])
        else:
            logging.info("userid NOT FOUND in json")
            return self.render_json_response(
                authorization = True,
                success = False,
                response_message = "userid is required"
            )


        gpController = GamePlayersController()
        mtsController = MatchTaskStatusController()
        mpController = MatchPlayersController()
        gmController = GameModesController()
        matchController = MatchController()

        user = UsersController().get_by_key_id(userid)

        if not user:
            logging.info('user not found.')
            return self.render_json_response(
                authorization = True,
                success = False,
                response_message = "user was not found"
            )


        ## update the match player to be disabled for matchmaker
        ## prevent them from showing up in the task
        match_player = mpController.get_join_pending_by_gameKeyId_userKeyId(int(gameKeyId), userid)

        if not match_player:
            logging.error('no match player found, this should not be possible.')
            return self.render_json_response(
                authorization = True,
                success = False,
                response_message = "match_player was not found"
            )

        if match_player.matchKeyId:
            logging.info('matchKeyId found')
            ## TODO look up the match data, specifically the session data to pass down

            match = matchController.get_by_key_id(match_player.matchKeyId)
            if not match.match_active:
                match.match_active = True
                matchController.update(match)

            return self.render_json_response(
                authorization = True,
                success = True,
                key_id = match_player.matchKeyId,
                matchmakerStarted = match_player.matchmakerStarted,
                matchmakerPending = match_player.matchmakerPending,
                matchmakerFoundMatch = match_player.matchmakerFoundMatch,
                matchmakerFinished = match_player.matchmakerFinished,
                matchmakerServerReady = match_player.matchmakerServerReady,
                matchmakerJoinable = match_player.matchmakerJoinable,
                session_host_address = match.hostConnectionLink or "",
                session_id = match.session_id or "",
            )
        else:
            return self.render_json_response(
                authorization = True,
                success = True,
                key_id = match_player.matchKeyId,
                matchmakerStarted = match_player.matchmakerStarted,
                matchmakerPending = match_player.matchmakerPending,
                matchmakerFoundMatch = match_player.matchmakerFoundMatch,
                matchmakerFinished = match_player.matchmakerFinished,
                matchmakerServerReady = match_player.matchmakerServerReady,
                matchmakerJoinable = match_player.matchmakerJoinable,
                session_host_address = "",
                session_id = "",
            )
