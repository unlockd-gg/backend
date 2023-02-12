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
from apps.uetopia.controllers.servers import ServersController
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
        serverKeyId = self.request.get('serverKeyId')

        logging.info('project: ' + project)
        logging.info('zone: ' + zone)
        logging.info('name: ' + name)



        ## update firebase

        entity = ServersController().get_by_key_id(int(serverKeyId))
        server_title = ""

        if entity:
            server_title = entity.title
            if not entity.invisible:
                logging.info('visible')
                if not entity.invisible_developer_setting:
                    logging.info('visible-dev')
                    taskUrl='/task/server/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': entity.key.id()}, countdown = 2,)


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

            ## STOP HERE?
            ## We don't need to send discord pushes if it was really offline.

            ## just keep it for now...
            ## return

        game = GamesController().get_by_key_id(entity.gameKeyId)

        ## do slack/discord pushes if enabled
        if game.slack_subscribe_vm_activity and game.slack_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Server VM Deallocate: %s | %s" % ( name, zone)
            slack_data = {'text': message}
            data=json.dumps(slack_data)
            resp, content = http_auth.request(game.slack_webhook,
                              "POST",
                              data,
                              headers=headers)

        if game.discord_subscribe_vm_activity and game.discord_webhook_admin:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Server VM Deallocate: %s | %s | %s" % ( server_title, name, zone)
            title = "%s Deallocate" % (server_title)
            url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
            discord_data = { "embeds": [{"title": title, "url": url, "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)
