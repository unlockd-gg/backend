import logging
import datetime
import string
import json
from httplib2 import Http

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.group_raids import GroupRaidsController
from apps.uetopia.controllers.group_raid_members import GroupRaidMembersController
from apps.uetopia.controllers.team_members import TeamMembersController
from apps.uetopia.controllers.groups import GroupsController
from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.group_games import GroupGamesController
from apps.uetopia.controllers.group_game_users import GroupGameUsersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


class serverGroupGKPEndHandler(BaseHandler):
    def post(self):
        """
        End a GKP session
        Requires http headers:  Key, Sign
        Requires JSON parameters:  nonce, list of group_gkp_members
        """

        serverController = ServersController()
        ucontroller = UsersController()
        spController = ServerPlayersController()
        transactionController = TransactionsController()
        lockController = TransactionLockController()
        teamMemberController = TeamMembersController()
        groupRaidController = GroupRaidsController()
        groupRaidMemberController = GroupRaidMembersController()
        groupController = GroupsController()
        groupRoleController = GroupRolesController()
        groupUserController = GroupUsersController()
        groupGameController = GroupGamesController()
        groupGameUserController = GroupGameUsersController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

        try:
            id_token = self.request.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')

        if id_token:
            logging.info("id_token: %s" %id_token)

            ## With a token we don't need all of this auto-auth garbage
            # Verify Firebase auth.
            #logging.info(self.request_state)

            claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
            if not claims:
                logging.error('Firebase Unauth')
                return self.render_json_response(
                    authorization = True,
                    player_authorized = False,
                    user_key_id = incoming_userid,
                    player_userid = incoming_userid,
                )

            authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

            if not authorized_user:
                logging.info('no user record found')
                return self.render_json_response(
                    authorization = True,
                    player_authorized = False,
                    user_key_id = incoming_userid,
                    player_userid = incoming_userid,
                )
        else:

            return self.render_json_response(
                authorization = True,
                success=False,
            )

        ## we use json for incoming params

        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)
        ## encryption = jsonobject["encryption"]

        if 'processAsValid' not in jsonobject:
            logging.info(" processAsValid was not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                error_message = " processAsValid was not found in json",
                userKeyId = str(authorized_user.key.id())
            )

        ## also incoming should be the list of userIDs and the new GKP values for them.
        if 'group_raid_members' not in jsonobject:
            logging.info(" group_raid_members was not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                error_message = " group_raid_members was not found in json",
                userKeyId = str(authorized_user.key.id())
            )



        ## get the party for this user
        auth_team_member = teamMemberController.get_by_gameKeyId_userKeyId(server.gameKeyId, authorized_user.key.id() )

        if not auth_team_member:
            logging.info('no auth_team_member record found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "no auth_team_member record found",
                userKeyId = str(authorized_user.key.id())
            )

        ## make sure the user is captain
        if not auth_team_member.captain:
            logging.info(' auth_team_member is not captain')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "auth_team_member is not captain",
                userKeyId = str(authorized_user.key.id())
            )

        # get the current team members
        all_team_members = teamMemberController.get_by_teamKeyId(auth_team_member.teamKeyId)

        ## TODO - make sure there is not an active raid already

        ## make sure the player making the request has the correct permissions in the group "raid_lead"
        auth_user_group_membership = groupUserController.get_by_groupKeyId_userKeyId(authorized_user.groupTagKeyId, authorized_user.key.id())
        if not auth_user_group_membership:
            logging.info('auth_user_group_membership not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "auth_user_group_membership not found",
                userKeyId = str(authorized_user.key.id())
            )

        ## get the group user role
        auth_user_group_role = groupRoleController.get_by_key_id(auth_user_group_membership.roleKeyId)
        if not auth_user_group_role:
            logging.info('auth_user_group_role not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "auth_user_group_role not found",
                userKeyId = str(authorized_user.key.id())
            )

        if not auth_user_group_role.raid_lead:
            logging.info('User is missing the raid lead permission')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "User is missing the raid lead permission",
                userKeyId = str(authorized_user.key.id())
            )

        ## get the auth user group raid membership
        auth_user_group_raid_membership = groupRaidMemberController.get_active_by_userKeyId(authorized_user.key.id())
        if not auth_user_group_raid_membership:
            logging.info('auth_user_group_raid_membership not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "auth_user_group_raid_membership not found",
                userKeyId = str(authorized_user.key.id())
            )

        ## get the raid
        group_raid = groupRaidController.get_by_key_id(auth_user_group_raid_membership.groupRaidKeyId)
        if not group_raid:
            logging.info('group_raid not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "group_raid not found",
                userKeyId = str(authorized_user.key.id())
            )

        ## make sure the raid itself is not finalized
        if group_raid.finalized:
            logging.info('group_raid is already finalized')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "group_raid is already finalized",
                userKeyId = str(authorized_user.key.id())
            )

        ## get the raid members
        group_raid_members = groupRaidMemberController.list_by_groupRaidKeyId(group_raid.key.id() )


        if not jsonobject['processAsValid']:
            logging.info('the raid was not valid - deleting')

            ## just delete it all for now.
            ## TODO - consider keeping invalid stuff?

            for group_raid_member in group_raid_members:
                groupRaidMemberController.delete(group_raid_member)

            groupRaidController.delete(group_raid)

            return self.render_json_response(
                authorization = True,
                success=True,
                error_message = "Success:  Raid invalidated and removed.",
                userKeyId = str(authorized_user.key.id())
            )

        ## process the raid as valid

        logging.info('processing raid as valid')

        group_raid.complete = True
        group_raid.completedTime = datetime.datetime.now()

        ## match up the raid_members in the incoming json to the group_raid_members

        for group_raid_member in group_raid_members:
            logging.info('checking raid member')

            found_match_in_json = False

            for grm_json in jsonobject['group_raid_members']:
                logging.info('checking json')

                if grm_json['userKeyId'] == str(group_raid_member.userKeyId):
                    logging.info('found match')
                    found_match_in_json = True

                    group_raid_member.gkpAmount = grm_json['gkpAmount']
                    group_raid_member.gkpVettingRemaining = grm_json['gkpVettingRemaining']
                    group_raid_member.raidActive = False

                    groupRaidMemberController.update(group_raid_member)

                    ## also update the group game user
                    group_game_user = groupGameUserController.get_by_groupKeyId_userKeyId_gameKeyId(group_raid.groupKeyId, group_raid_member.userKeyId, group_raid.gameKeyId)

                    if group_game_user:
                        logging.info('updating group game user')
                        group_game_user.gkpAmount = grm_json['gkpAmount']
                        group_game_user.gkpVettingRemaining = grm_json['gkpVettingRemaining']

                        groupGameUserController.update(group_game_user)


        ## update the raid and set inactive

        group_raid.finalized = True
        group_raid.finalizedTime = datetime.datetime.now()

        groupRaidController.update(group_raid)



        return self.render_json_response(
            authorization = True,
            success=True,
            error_message = "Success:  Group gkp session ended.",
            userKeyId = str(authorized_user.key.id())
        )
