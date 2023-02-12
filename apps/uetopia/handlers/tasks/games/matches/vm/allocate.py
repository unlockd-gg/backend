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
from apps.uetopia.controllers.server_links import ServerLinksController

from configuration import *

requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class TaskAllocate(BaseHandler):
    """
    Allocate a Google Compute Engine Instance.

    Incoming: matchKeyId required.

    """
    def post(self):
        """

        """
        logging.info('TaskAllocate')

        #serverController = ServersController()
        matchController = MatchController()
        gameController = GamesController()
        #serverLinksController = ServerLinksController()

        credentials = GoogleCredentials.get_application_default()
        compute = discovery.build('compute', 'v1', credentials=credentials)

        matchKeyId = self.request.get('matchKeyId', None)

        logging.info('matchKeyId: ' + matchKeyId)

        match = matchController.get_by_key_id(int(matchKeyId))
        if not match:
            logging.error('match not found with the specified key_id')
            return

        game = gameController.get_by_key_id(match.gameKeyId)
        if not game:
            logging.error('game not found with the specified key_id')
            return

        match.continuous_server_creating = True
        match.continuous_server_creating_timestamp = datetime.datetime.now()
        matchController.update(match)

        ## TODO check for provisioned server thet is currently vacant
        ## TODO check server pool to see if there is a non-provisioned server record that can be reused

        if not game.match_deploy_vm_source_disk_image:
            logging.error('Disk image not specified in game settings')
            return

        source_disk_image = "global/images/" + game.match_deploy_vm_source_disk_image
        machine_type = "zones/%s/machineTypes/%s" % (match.continuous_server_zone, game.match_deploy_vm_machine_type)
        ##startup_script = "screen /uetopia/MMDEMO1_LINUX/LinuxNoEditor/MMDEMO1/Binaries/Linux/MMDEMO1Server"
        image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
        image_caption = "Ready for dessert?"
        bucket = "ue4topia"
        name = "m" + str(match.key.id())
        ## In case we haven't configured this server use the default zone
        if match.continuous_server_zone:
            logging.info('found match.continuous_server_zone')
            server_dyn_zone = match.continuous_server_zone
        else:
            logging.info('DID NOT FIND match.continuous_server_zone - reverting to US CENTRAL')
            server_dyn_zone = "us-central1-b"

        diskType = "projects/" + game.match_deploy_vm_project + "/zones/" + server_dyn_zone + "/diskTypes/pd-ssd"
        diskSizeGb = "10"


        config = {
            'name': name,
            'machineType': machine_type,

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                        'diskType': diskType,
                        'diskSizeGb': diskSizeGb
                    }
                }
            ],

            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            # Allow the instance to access cloud storage and logging.
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'
                ]
            }],

            # Metadata is readable from the instance and allows you to
            # pass configuration from deployment scripts to instances.
            'metadata': {
                'items': [{
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    'key': 'startup-script-url',
                    'value': game.match_deploy_vm_startup_script_location
                }, {
                    'key': 'shutdown-script-url',
                    'value': game.match_deploy_vm_shutdown_script_location
                }, {
                    'key': 'url',
                    'value': image_url
                }, {
                    'key': 'UEtopiaMode',
                    'value': "competitive"
                }, {
                    'key': 'matchKeyId',
                    'value': matchKeyId
                },{
                    'key': 'matchApiKey',
                    'value': match.apiKey
                },{
                    'key': 'matchApiSecret',
                    'value': match.apiSecret
                }, {
                    'key': 'bucket',
                    'value': game.match_deploy_vm_bucket
                }]
            }
        }



        result = compute.instances().insert(
            project=game.match_deploy_vm_project,
            zone=server_dyn_zone,
            body=config).execute()

        logging.info(result)

        ## start a task to monitor the request for completion
        taskUrl='/task/matchmaker/vm/waitfordone'
        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': game.match_deploy_vm_project,
                                                                                "zone": server_dyn_zone,
                                                                                "operation": result['name'],
                                                                                "tries": 0,
                                                                                "name": name,
                                                                                "matchKeyId": matchKeyId
                                                                            }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DONE_DELAY_SECONDS)

        ## start a task to check on the server - this is in the case that no users activate or deactivate.
        taskUrl='/task/matchmaker/vm/checkunused'
        taskqueue.add(url=taskUrl, queue_name='matchCheckUnused', params={"matchKeyId": match.key.id()
                                                                            }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_UNUSED_SECONDS)

        ## do slack/discord pushes if enabled
        if game.slack_subscribe_vm_activity and game.slack_webhook:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Match VM Allocate: %s | %s" % ( name, match.continuous_server_zone)
            slack_data = {'text': message}
            data=json.dumps(slack_data)
            resp, content = http_auth.request(game.slack_webhook,
                              "POST",
                              data,
                              headers=headers)

        if game.discord_subscribe_vm_activity and game.discord_webhook_admin:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            message = "Match VM Allocate: %s | %s" % ( name, match.continuous_server_zone)
            url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
            discord_data = { "embeds": [{"title": "Match VM Allocate", "url": url, "description": message}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(game.discord_webhook_admin,
                              "POST",
                              data,
                              headers=headers)
