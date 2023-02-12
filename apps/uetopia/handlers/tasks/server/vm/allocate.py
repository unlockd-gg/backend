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
##from google.appengine.api import users
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.server_clusters import ServerClustersController

from configuration import *

requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class TaskAllocate(BaseHandler):
    """
    Allocate a Google Compute Engine Instance.

    Incoming: serverKeyId required.

    """
    def post(self):
        """

        """
        logging.info('TaskAllocate')

        serverController = ServersController()
        serverLinksController = ServerLinksController()
        userController = UsersController()
        chatChannelsController = ChatChannelsController()
        serverClusterController = ServerClustersController()

        credentials = GoogleCredentials.get_application_default()
        compute = discovery.build('compute', 'v1', credentials=credentials)


        serverKeyId = self.request.get('serverKeyId', None)


        logging.info('serverKeyId: ' + serverKeyId)

        server = serverController.get_by_key_id(int(serverKeyId))
        if not server:
            logging.error('server not found with the specified key_id')
            return

        server.continuous_server_creating = True
        server.continuous_server_creating_timestamp = datetime.datetime.now()


        ## TODO check for provisioned server thet is currently vacant
        ## TODO check server pool to see if there is a non-provisioned server record that can be reused

        vm_disk_image = None

        ## if this is a continuous server - get all of the VM details from server cluster
        if server.continuous_server:
            server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)

            vm_project = server_cluster.vm_project
            vm_bucket = server_cluster.vm_bucket
            vm_region = server_cluster.vm_region
            vm_zone = server_cluster.vm_zone
            vm_disk_image = server_cluster.vm_disk_image
            vm_machine_type = server_cluster.vm_machine_type
            vm_startup_script_location = server_cluster.vm_startup_script_location
            vm_shutdown_script_location = server_cluster.vm_shutdown_script_location


        if vm_disk_image:
            source_disk_image = "global/images/" + vm_disk_image
            machine_type = "zones/%s/machineTypes/%s" % (vm_zone, vm_machine_type)
            ##startup_script = "screen /uetopia/MMDEMO1_LINUX/LinuxNoEditor/MMDEMO1/Binaries/Linux/MMDEMO1Server"
            image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
            image_caption = "Ready for dessert?"
            bucket = "ue4topia"
            name = "a" + str(server.key.id())


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
                        'value': vm_startup_script_location
                    }, {
                        'key': 'shutdown-script-url',
                        'value': vm_shutdown_script_location
                    }, {
                        'key': 'url',
                        'value': image_url
                    }, {
                        'key': 'UEtopiaMode',
                        'value': "continuous"
                    }, {
                        'key': 'serverKeyId',
                        'value': serverKeyId
                    },{
                        'key': 'serverApiKey',
                        'value': server.apiKey
                    },{
                        'key': 'serverApiSecret',
                        'value': server.apiSecret
                    }, {
                        'key': 'bucket',
                        'value': vm_bucket
                    }]
                }
            }

            ## In case we haven't configured this server use the default zone
            if vm_zone:
                server_dyn_zone = vm_zone
            else:
                server_dyn_zone = "us-central1-b"

            ## Compute engine can error out here in several ways.

            ## sometimes we see
            ## HttpError: <HttpError 409 when
            ## requesting https://www.googleapis.com/compute/v1/projects/ue4topia/zones/us-central1-b/instances?alt=json
            ## returned "The resource 'projects/ue4topia/zones/us-central1-b/instances/a5641142922117120' already exists">

            ## just log it and pass
            try:
                result = compute.instances().insert(
                    project=vm_project,
                    zone=server_dyn_zone,
                    body=config).execute()

                logging.info(result)
            except:
                result = None
                logging.error('there was a compute engine error.')

            if result:
                ##  update server links with the new hostConnectionLink
                target_server_links = serverLinksController.get_list_by_targetServerKeyId(server.key.id())
                for link in target_server_links:
                    link.targetStatusCreating = True
                    serverLinksController.update(link)

                ## start a task to monitor the request for completion
                taskUrl='/task/server/vm/waitfordone'
                taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': vm_project,
                                                                                        "zone": server_dyn_zone,
                                                                                        "operation": result['name'],
                                                                                        "tries": 0,
                                                                                        "name": name,
                                                                                        "serverKeyId":serverKeyId
                                                                                    }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DONE_DELAY_SECONDS)

                ## start a task to check on the server - this is in the case that no users activate or deactivate.
                taskUrl='/task/server/vm/checkunused'
                checkUnusedTask = taskqueue.add(url=taskUrl, queue_name='serverCheckUnused', params={"serverKeyId": server.key.id()
                                                                                    }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_UNUSED_SECONDS)

                server.checkUnusedTaskName = checkUnusedTask.name
                serverController.update(server)

                ## send text chat if this is an instanced server
                if server.instanced_from_template:
                    if server.instance_server_configuration == 'user':
                        logging.info('this is an instanced user server - sending chat')

                        ## get the user:
                        server_instance_user = userController.get_by_key_id(server.instanced_for_userKeyId)
                        if server_instance_user:
                            chat_message = "> Private server %s starting up" %server.title
                            taskUrl='/task/chat/send'
                            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': server_instance_user.firebaseUser,
                                                                                                "message": chat_message,
                                                                                                "created":datetime.datetime.now().isoformat()
                                                                                            })
                    elif server.instance_server_configuration == 'party':
                        logging.info('this is an instanced party server - sending chat')

                        # get the party chat channel
                        party_chat_channel = chatChannelsController.get_by_channel_type_refKeyId('team', server.instanced_for_partyKeyId)
                        if party_chat_channel:
                            chat_message = "Party server %s starting up" %server.title

                            taskUrl='/task/chat/channel/send'
                            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': party_chat_channel.key.id(),
                                                                                                "message": chat_message,
                                                                                                #"userKeyId": authorized_user.key.id(),
                                                                                                #"userTitle": authorized_user.title,
                                                                                                "chatMessageKeyId": uuid.uuid4(),
                                                                                                "chatChannelTitle": party_chat_channel.title,
                                                                                                "chatChannelRefType":party_chat_channel.channel_type,
                                                                                                "created":datetime.datetime.now().isoformat()
                                                                                            })
                    elif server.instance_server_configuration == 'group':
                        logging.info('this is an instanced group server - sending chat')

                        # get the party chat channel
                        group_chat_channel = chatChannelsController.get_by_channel_type_refKeyId('group', server.instanced_for_groupKeyId)
                        if group_chat_channel:
                            chat_message = "Group server %s starting up" %server.title

                            taskUrl='/task/chat/channel/send'
                            taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'key_id': group_chat_channel.key.id(),
                                                                                                "message": chat_message,
                                                                                                #"userKeyId": authorized_user.key.id(),
                                                                                                #"userTitle": authorized_user.title,
                                                                                                "chatMessageKeyId": uuid.uuid4(),
                                                                                                "chatChannelTitle": group_chat_channel.title,
                                                                                                "chatChannelRefType": group_chat_channel.channel_type,
                                                                                                "created": datetime.datetime.now().isoformat()
                                                                                            })



                game = GamesController().get_by_key_id(server.gameKeyId)
                if game:
                    ## do slack/discord pushes if enabled
                    if game.slack_subscribe_vm_activity and game.slack_webhook:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "Server VM Allocate: %s | %s" % ( name, server_dyn_zone)
                        slack_data = {'text': message}
                        data=json.dumps(slack_data)
                        resp, content = http_auth.request(game.slack_webhook,
                                          "POST",
                                          data,
                                          headers=headers)

                    if game.discord_subscribe_vm_activity and game.discord_webhook_admin:
                        http_auth = Http()
                        headers = {"Content-Type": "application/json"}
                        message = "Server VM Allocate: %s | %s | %s" % ( server.title, name, server_dyn_zone)
                        message_title = "%s Allocate" % (server.title)
                        url = "http://ue4topia.appspot.com/#/developer/game/%s" % game.key.id()
                        discord_data = { "embeds": [{"title": message_title, "url": url, "description": message}] }
                        data=json.dumps(discord_data)
                        resp, content = http_auth.request(game.discord_webhook_admin,
                                          "POST",
                                          data,
                                          headers=headers)
        else:
            logging.info('VM disk image not set up - sending discord notification for dev/testing')

            game = GamesController().get_by_key_id(server.gameKeyId)
            if game:

                if game.discord_subscribe_errors and game.discord_webhook_admin:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    message = "Simulating server allocation.  %s server can be started at this time.  Mark the server as provisioned manually." % (server.title)
                    discord_data = { "embeds": [{"title": "Server allocation", "url": "https://example.com", "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(game.discord_webhook_admin,
                                      "POST",
                                      data,
                                      headers=headers)
