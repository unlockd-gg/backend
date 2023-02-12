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
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.users import UsersController
#from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.server_links import ServerLinksController

from configuration import *

class TaskWaitForDone(BaseHandler):
    """


    """
    def post(self):
        """

        """


        matchController = MatchController()
        #mpController = MatchPlayersController()

        credentials = GoogleCredentials.get_application_default()
        compute = discovery.build('compute', 'v1', credentials=credentials)

        project = self.request.get('project')
        operation = self.request.get('operation')
        tries = self.request.get('tries')
        name = self.request.get('name')
        matchKeyId = self.request.get('matchKeyId')

        ## get the match
        match = matchController.get_by_key_id(int(matchKeyId))
        if not match:
            logging.error('match not found with the specified key_id')
            return

        logging.info('project: ' + project)
        logging.info('operation: ' + operation)
        logging.info('tries: ' + tries)
        logging.info('name: ' + name)
        logging.info('matchKeyId: ' + matchKeyId)

        logging.info('Waiting for operation to finish...')
        result = compute.zoneOperations().get(
            project=project,
            zone=match.continuous_server_zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            logging.info("done.")
            if 'error' in result:
                logging.error(result['error'])
                return result
            ## grab the ip address
            filteri = "name eq %s" % name
            logging.info('filteri: ' + filteri)
            instances = compute.instances().list(zone=match.continuous_server_zone, project=project, filter=filteri).execute()
            logging.info(instances['items'])
            logging.info("len instances: %s" %len(instances['items']))
            logging.info(instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP'])

            match.continuous_server_provisioned = True
            match.continuous_server_title = name
            #match.matchmaker_dynamic_server_zone = match.dynamic_server_zone

            match.hostAddress = instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP']
            match.hostPort = "7777"
            match.hostConnectionLink = instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP'] + ":7777"

            match.continuous_server_creating = False
            match.continuous_server_provisioned = True
            match.continuous_server_active = True
            match.continuous_server_project = project

            matchController.update(match)



        else:
            ## TODO fire off a new task to check later
            logging.info("not done yet.")

            tries = str(int(tries)+1)

            ## start a task to monitor the request for completion
            taskUrl='/task/matchmaker/vm/waitfordone'
            taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': 'ue4topia',
                                                                                    "operation": result['name'],
                                                                                    "tries": tries,
                                                                                    "name": name,
                                                                                    "matchKeyId": matchKeyId
                                                                                }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DONE_DELAY_SECONDS)
