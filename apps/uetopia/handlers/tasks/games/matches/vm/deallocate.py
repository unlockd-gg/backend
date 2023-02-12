import logging
import re
import os
import datetime
import json
import uuid

import google.oauth2.id_token
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine
from httplib2 import Http
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController

from configuration import *

requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class TaskDeallocate(BaseHandler):
    """


    """
    def post(self):
        """

        """
        logging.info('TaskDeallocate')

        credentials = GoogleCredentials.get_application_default()
        compute = discovery.build('compute', 'v1', credentials=credentials)

        project = self.request.get('project')
        zone = self.request.get('zone')
        name = self.request.get('name')
        matchKeyId = self.request.get('matchKeyId')

        logging.info('project: ' + project)
        logging.info('zone: ' + zone)
        logging.info('name: ' + name)
        logging.info('matchKeyId: ' + matchKeyId)

        ## just try to delete it.
        ## it may already have been deleted, so accept the error
        try:
            result = compute.instances().delete(
                    project=project,
                    zone=zone,
                    instance=name).execute()


            logging.info(result)
        except:
            logging.error('VM delete error')

        ## TODO update firebase

        match = MatchController().get_by_key_id(int(matchKeyId))

        if match:
            game = GamesController().get_by_key_id(match.gameKeyId)

            ## update match - this should already be done!
            #match.match_destroying = True
            #match_destroying_timestamp = datetime.datetime.now()

            ## do slack/discord pushes if enabled
            if game.slack_subscribe_vm_activity and game.slack_webhook:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Match VM Deallocate: %s | %s" % ( name, zone)
                slack_data = {'text': message}
                data=json.dumps(slack_data)
                resp, content = http_auth.request(game.slack_webhook,
                                  "POST",
                                  data,
                                  headers=headers)

            if game.discord_subscribe_vm_activity and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "Match VM Deallocate: %s | %s" % ( name, zone)
                url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                discord_data = { "embeds": [{"title": "Match VM Deallocate", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)
