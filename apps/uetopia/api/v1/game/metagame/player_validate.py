import logging
import datetime
import string
import json
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController
from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController
from configuration import *

class gamePlayerValidateHandler(BaseHandler):
    def post(self):
        """
        Send game player
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, securityCode
        """

        serverController = ServersController()
        ucontroller = UsersController()
        gpController = GamePlayersController()
        gameController = GamesController()
        #gameCharacterController = GameCharactersController()
        teamMembersController = TeamMembersController()
        #gamePlayerSnapshotController = GamePlayerSnapshotController()
        groupsController = GroupsController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGameController = GroupGamesController()

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

        game_player = gpController.get_by_api_key(self.request.get('securityCode') )
        if not game_player:
            logging.info("The game player was not found.")
            return self.render_json_response(
                authorization = True,
                player_key_id = None,
                team_key_id = None,
                team_title = None,
                team_captain = None,
                group_key_id = None,
                group_tag = None,
                error= "The game player was not found.  Launch the game client and login first.",
                request_successful = False
                )

        ## only allow connecting once.
        if game_player.metagame_connected:
            logging.info("The game player is already connected.")
            return self.render_json_response(
                authorization = True,
                player_key_id = None,
                team_key_id = None,
                team_title = None,
                team_captain = None,
                group_key_id = None,
                group_tag = None,
                error= "The game player is already connected.",
                request_successful = False
                )


        ## TODO - any other checks?

        game_player.metagame_connected = True
        game_player.apiKey = None

        gpController.update(game_player)



        team_key_id = None
        team_title = None
        team_captain = False
        group_key_id = None
        group_tag = None
        group_iconUrl = None

        ## also send back information about the current party and group
        team_member = teamMembersController.get_by_gameKeyId_userKeyId(game.key.id(), game_player.userKeyId)

        if team_member:
            logging.info('found team member')
            team_key_id = team_member.teamKeyId
            team_title = team_member.teamTitle
            team_captain = team_member.captain

        ## to get the group, we need the user account. get that first
        game_player_user = ucontroller.get_by_key_id(game_player.userKeyId)

        metagame_team_lead = None
        metagame_faction_lead = None

        if game_player_user:
            group_key_id = game_player_user.groupTagKeyId


            if game_player_user.groupTagKeyId:
                ## get the group member so that we can get the role associated.
                group_member = groupUserController.get_by_groupKeyId_userKeyId(game_player_user.groupTagKeyId, game_player_user.key.id())
                if group_member:
                    logging.info('The group member was found.')

                    ## get the group member's role
                    group_member_role = groupRoleController.get_by_key_id(group_member.roleKeyId)
                    if group_member_role:
                        logging.info('The group member role was found.')

                        metagame_team_lead = group_member_role.metagame_team_lead
                        metagame_faction_lead = group_member_role.metagame_faction_lead

                    ## Get the group itself
                    group = groupsController.get_by_key_id(game_player_user.groupTagKeyId)
                    if group:
                        logging.info('found group')
                        group_iconUrl = group.iconServingUrl
                        group_tag = "[" + group.tag + "]"

        return self.render_json_response(
            authorization = True,
            request_successful=True,
            player_key_id = game_player.key.id(),
            team_key_id = team_key_id,
            team_title = team_title,
            team_captain = team_captain,
            group_key_id = group_key_id,
            group_tag = group_tag,
            group_icon_url = group_iconUrl,
            metagame_team_lead = metagame_team_lead,
            metagame_faction_lead = metagame_faction_lead,

        )
