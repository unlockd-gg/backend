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


class serverGroupGKPStartHandler(BaseHandler):
    def post(self):
        """
        Start a new GKP session
        Requires http headers:  Key, Sign
        Requires JSON parameters:  nonce, amount, description
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

        if 'title' not in jsonobject:
            logging.info(" title was not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                error_message = " title was not found in json",
                userKeyId = str(authorized_user.key.id())
            )

        if 'description' not in jsonobject:
            logging.info("description was not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                error_message = " description was not found in json",
                userKeyId = str(authorized_user.key.id())
            )

        if 'vettingEnabled' not in jsonobject:
            logging.info("vettingEnabled was not found in json")
            return self.render_json_response(
                authorization = True,
                success=False,
                error_message = " vettingEnabled was not found in json",
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
                error_message = "Could not find your party/team record.  Try reforming the party.",
                userKeyId = str(authorized_user.key.id())
            )

        ## make sure the user is captain
        if not auth_team_member.captain:
            logging.info(' auth_team_member is not captain')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "You are not the captain of this party.  Only the captain can start GKP.",
                userKeyId = str(authorized_user.key.id())
            )


        ## make sure there is not an active raid already
        existing_active_group_raid_member = groupRaidMemberController.get_active_by_userKeyId(authorized_user.key.id())
        if existing_active_group_raid_member:
            logging.info('existing_active_group_raid_member found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "Existing Raid found.  Delete or end the existing one if you want to create a new one.",
                userKeyId = str(authorized_user.key.id())
            )

        # get the current team members
        all_team_members = teamMemberController.get_by_teamKeyId(auth_team_member.teamKeyId)



        ## make sure the player making the request has the correct permissions in the group "raid_lead"
        auth_user_group_membership = groupUserController.get_by_groupKeyId_userKeyId(authorized_user.groupTagKeyId, authorized_user.key.id())
        if not auth_user_group_membership:
            logging.info('auth_user_group_membership not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "Could not find your group membership.  GKP only works with groups.  Are you a member of a group?  Is it selected in your profile?",
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
                error_message = "Could not find your group role.  Contact your group admin to reassign one.",
                userKeyId = str(authorized_user.key.id())
            )

        if not auth_user_group_role.raid_lead:
            logging.info('User is missing the raid lead permission')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "You do not have the raid lead permission.  Contact your group admin to assign the permission.",
                userKeyId = str(authorized_user.key.id())
            )

        ## get the group
        group = groupController.get_by_key_id(authorized_user.groupTagKeyId)
        if not group:
            logging.info('group not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "Group not found.  GKP only works with groups.  Are you a member of a group?  Is it selected in your profile?",
                userKeyId = str(authorized_user.key.id())
            )

        ## make sure the groupGame Exists
        group_game =groupGameController.get_by_groupKeyId_gameKeyId(group.key.id(), server.gameKeyId)
        if not group_game:
            logging.info('group_game not found')
            return self.render_json_response(
                authorization = True,
                player_authorized = True,
                success=False,
                error_message = "Group game not found.  Contact your group admin to add the game to the group.",
                userKeyId = str(authorized_user.key.id())
            )



        ## any other checks here?

        ## set up the new raid and members.
        group_raid = groupRaidController.create(
            groupKeyId = group.key.id(),
            groupTitle = group.title,

            gameKeyId = server.gameKeyId,
            gameTitle = server.gameTitle,

            teamKeyId = auth_team_member.teamKeyId,
            teamTitle = auth_team_member.teamTitle,

            captainKeyId = authorized_user.key.id(),
            captainTitle = authorized_user.title,

            title = jsonobject['title'],
            description = jsonobject['description'],

            started = True,
            complete = False,
            finalized = False,
            ## TODO add more group permissions

            #startedTime = ndb.DateTimeProperty()
            #completedTime = ndb.DateTimeProperty()
            #finalizedTime = ndb.DateTimeProperty()

            vettingEnabled = jsonobject['vettingEnabled'],
            vettingCompleted = False
        )


        ## keep track of the team members that should have a GKP account created...  This saves another round of lookups.
        gkp_team_members = []
        gkp_group_members = []
        group_raid_members_json = []

        for team_member in all_team_members:
            logging.info('checking team member for group game membership')



            team_member_group_membership = groupUserController.get_by_groupKeyId_userKeyId(authorized_user.groupTagKeyId, team_member.userKeyId)
            if team_member_group_membership:
                ## user is a mamber of this group.

                ## doing this in group game users now, because I want seperate gkp for every game.

                group_game_user = groupGameUserController.get_by_groupKeyId_userKeyId_gameKeyId(authorized_user.groupTagKeyId, team_member.userKeyId, server.gameKeyId)

                if not group_game_user:
                    logging.info('checking team member for group game membership did not exist.  Creating it.')

                    group_game_user = groupGameUserController.create(
                        groupKeyId = authorized_user.groupTagKeyId,
                        #groupTitle = ndb.StringProperty()

                        gameKeyId = server.gameKeyId,
                        gameTitle = server.gameTitle,

                        userKeyId = team_member.userKeyId,
                        userTitle = team_member.userTitle,

                        groupUserKeyId = team_member_group_membership.key.id(),

                        vettingEnabled = True,
                        vettingCompleted = False,
                        vettingFinalized = False,

                        gkpAmount = 0,
                        gkpVettingRemaining = 4
                    )

                # set up the vetting settings here?
                if jsonobject['vettingEnabled']:
                    logging.info('vettingEnabled')

                    if group_game_user.gkpVettingRemaining > 0:
                        logging.info('group_game_user has vetting remaining')

                        gkpVettingRemaining = group_game_user.gkpVettingRemaining -1
                        gkpAmount = group_game_user.gkpAmount + 25
                        gkpVettingThisRaid = 25

                    else:
                        gkpVettingRemaining = 0
                        gkpAmount = group_game_user.gkpAmount
                        gkpVettingThisRaid =  0
                else:
                    gkpVettingRemaining = group_game_user.gkpVettingRemaining
                    gkpAmount = group_game_user.gkpAmount
                    gkpVettingThisRaid =  0





                group_raid_member = groupRaidMemberController.create(
                    groupKeyId = group.key.id(),
                    groupTitle = group.title,

                    gameKeyId = server.gameKeyId,
                    gameTitle = server.gameTitle,

                    teamKeyId = auth_team_member.teamKeyId,
                    teamTitle = auth_team_member.teamTitle,

                    captainKeyId = auth_team_member.userKeyId,
                    captainTitle = auth_team_member.userTitle,

                    groupRaidKeyId = group_raid.key.id(),
                    groupRaidTitle = group_raid.title,

                    userKeyId = team_member.userKeyId,
                    userTitle = team_member.userTitle,

                    vettingEnabled = group_raid.vettingEnabled,
                    vettingCompleted = False,
                    vettingFinalized = False,

                    gkpAmount = gkpAmount,
                    gkpAmountSpentThisRaid = 0,
                    gkpVettingThisRaid = gkpVettingThisRaid,
                    gkpVettingRemaining = gkpVettingRemaining,

                    raidActive = True
                )

                group_raid_members_json.append(group_raid_member.to_json())

            gkp_team_members.append(team_member)
            gkp_group_members.append(team_member_group_membership)

        else:
            logging.info('team member is not a member of the group.')

            ## TODO - send out a chat message to this user
            ## Warning.  You are not a member of this group.  You will not earn any GKP for this raid, and you will be unable to bid for loot.



        ## do this after the new raid is all set up
        ## check to see if the settings are set to run the vetting logic
        ## -- Users get 25 GKP allocated for each vetting stage, 4 times total.
        ## -- When they have reached 100 points allocated, vetting stops.
        ## vetting should apply at the start of the raid.

        ## any other checks here?  Check for existing open raid or something

        ## probably want to return the raid_members

        return self.render_json_response(
            authorization = True,
            success=True,
            error_message = "Success:  Group gkp started.",
            group_raid_members = group_raid_members_json,
            userKeyId = str(authorized_user.key.id())
        )
