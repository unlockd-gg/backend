import logging
import re
import os
import datetime
import json
import uuid

## Google oauth credentials for consuming google api services
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
#from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_clusters import ServerClustersController

from configuration import *

class TaskWaitForDone(BaseHandler):
    """


    """
    def post(self):
        """

        """


        serverController = ServersController()
        serverLinksController = ServerLinksController()
        serverClusterController = ServerClustersController()

        credentials = GoogleCredentials.get_application_default()
        compute = discovery.build('compute', 'v1', credentials=credentials)

        project = self.request.get('project')
        operation = self.request.get('operation')
        tries = self.request.get('tries')
        name = self.request.get('name')
        #matchKeyId = self.request.get('matchKeyId', None)
        serverKeyId = self.request.get('serverKeyId')

        ## get the server
        server = serverController.get_by_key_id(int(serverKeyId))
        if not server:
            logging.error('server not found with the specified key_id')
            return

        ## get the server cluster
        server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)

        logging.info('project: ' + project)
        logging.info('operation: ' + operation)
        logging.info('tries: ' + tries)
        logging.info('name: ' + name)
        #logging.info('matchKeyId: ' + matchKeyId)
        logging.info('serverKeyId: ' + serverKeyId)

        logging.info('Waiting for operation to finish...')
        result = compute.zoneOperations().get(
            project=project,
            zone=server_cluster.vm_zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            logging.info("done.")
            if 'error' in result:
                logging.error(result['error'])
                return result
            ## grab the ip address
            filteri = "name eq %s" % name
            logging.info('filteri: ' + filteri)
            instances = compute.instances().list(zone=server_cluster.vm_zone, project=project, filter=filteri).execute()
            logging.info(instances['items'])
            logging.info("len instances: %s" %len(instances['items']))
            logging.info(instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP'])
            ## update the uetopia server record

            ## get the match
            #try:
        #        if matchKeyId:
        #            match = matchController.get_by_key(matchKeyId)
    #                match.gameJoinLink = instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP'] + ":7777"
    #                matchController.update(match)
    #
    ##            logging.info("matchKeyId error")
    #            match = None

            server.continuous_server_provisioned = True
            server.continuous_server_title = name
            #server.matchmaker_dynamic_server_zone = server.dynamic_server_zone

            server.hostAddress = instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP']
            server.hostPort = "7777"
            server.hostConnectionLink = instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP'] + ":7777"

            server.continuous_server_creating = False
            server.continuous_server_provisioned = True
            server.continuous_server_active = True

            serverController.update(server)

            ##  update server links with the new hostConnectionLink
            target_server_links = serverLinksController.get_list_by_targetServerKeyId(server.key.id())
            for link in target_server_links:
                link.hostConnectionLink = server.hostConnectionLink
                link.targetStatusProvisioned = True
                ##link.targetStatusOnline = True
                ## moved online to the serverInfo request.  It can take 10-15 seconds between being provisioned to being ready to play.

                link.targetStatusCreating = False

                serverLinksController.update(link)



        else:
            ## TODO fire off a new task to check later
            logging.info("not done yet.")

            tries = str(int(tries)+1)

            ## start a task to monitor the request for completion
            taskUrl='/task/server/vm/waitfordone'
            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': 'ue4topia',
                                                                                    "operation": result['name'],
                                                                                    "tries": tries,
                                                                                    "name": name,
                                                                                    #"matchKeyId": matchKeyId,
                                                                                    "serverKeyId": serverKeyId
                                                                                }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DONE_DELAY_SECONDS)
