import logging
import datetime
import string
import json
import uuid
from httplib2 import Http
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GetUserTeamHandler(BaseHandler):
    def post(self):
        """
        Get team information for a user
        This is related to the UE concept of "party"
        But, the party data does not appear to be available to the server, only to the clients.
        This allows the server to query party/team information from the backend

        Requires http headers:  Key, Sign
        Requires POST parameters: nonce, userKeyId
        no access_token required.  This is server key/secret auth.
        """

        serverController = ServersController()
        uController = UsersController()

        teamController = TeamsController()
        teamMemberController = TeamMembersController()



        server = serverController.verify_signed_auth(self.request)

        if server == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('server auth success')

            # parse incoming json args
            jsonstring = self.request.body
            logging.info(jsonstring)
            jsonobject = json.loads(jsonstring)
            ## encryption = jsonobject["encryption"]

            if 'userKeyId' not in jsonobject:
                logging.info(" userKeyId was not found in json")
                return self.render_json_response(
                    authorization = True,
                    success=False
                )

            # get the user
            user = UsersController().get_by_key_id( int(jsonobject['userKeyId']) )

            if not user:
                logging.info('no user record found')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                    userKeyId = user.key.id()
                )
            # get the team member
            user_team_member = teamMemberController.get_by_gameKeyId_userKeyId(server.gameKeyId, user.key.id())
            if not user_team_member:
                logging.info('no user_team_member record found')
                return self.render_json_response(
                    authorization = True,
                    success = False,
                    userKeyId = user.key.id()
                )

            # get the current team members
            all_team_members = teamMemberController.get_by_teamKeyId(user_team_member.teamKeyId)

            team_members_response = []

            for t_member in all_team_members:
                ## skip self?  No just include
                #if s_shard.serverShardKeyId != server.key.id():
                team_members_response.append(t_member.to_json_userKeyIdStr() )

            ## do we need to include anything else about the general party/team?
            ## maybe just the title for display, but mostly we need the members


            return self.render_json_response(
                authorization = True,
                success = True,
                userKeyId = user.key.id(),
                team_members = team_members_response
            )
