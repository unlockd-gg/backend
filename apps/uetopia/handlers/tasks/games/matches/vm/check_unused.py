import logging
import re
import os
import datetime
import json
import uuid

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.match import MatchController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_instances import ServerInstancesController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from configuration import *

class TaskCheckUnused(BaseHandler):
    """


    """
    def post(self):
        """

        """
        logging.info('TaskCheckUnused')

        spController = ServerPlayersController()
        matchController = MatchController()
        mpController = MatchPlayersController()
        serverInstancesController = ServerInstancesController()
        serverLinksController = ServerLinksController()
        chatChannelController = ChatChannelsController()
        gameController = GamesController()

        matchKeyId = self.request.get('matchKeyId')


        ## TODO check to see if this match is part of an allocated match pool

        ## TODO check to see if the game has a specified pre-allocate amount

        ## TODO check to see if the game has a specific match cooldown


        match = matchController.get_by_key_id(int(matchKeyId))

        if not match:
            logging.info('Could not find the match - exiting')
            return

        game = gameController.get_by_key_id(match.gameKeyId)

        if not game:
            logging.info('Could not find the game - exiting')
            return

        ## prevent duplicate tasks
        if match.match_active == False:
            logging.info('active is false - exiting')
            return

        if game.match_timeout_max_minutes:
            timeout_duration_seconds = game.match_timeout_max_minutes * 60
        else:
            timeout_duration_seconds = 180 * 60


        ## If the match is totally stale, ignore the player states
        stale_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=timeout_duration_seconds)
        if match.created > stale_timestamp:
            logging.info('match is not stale')
            ## check to see if any of the players have connected
            match_players = mpController.get_list_by_matchKeyId(match.key.id())
            for match_player in match_players:
                logging.info('found match player')
                if match_player.joined:
                    logging.info('player is joined - exiting with requeue')

                    ## start a task to check on the server - this is in the case that not all users activate or deactivate.
                    taskUrl='/task/matchmaker/vm/checkunused'
                    taskqueue.add(url=taskUrl, queue_name='matchCheckUnused', params={"matchKeyId": match.key.id()
                                                                                        }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_UNUSED_SECONDS)
                    return


        created_datetime = match.created


        ## Here we want to set the active flag to false so that the deallocation process knows that we are done with it.
        ## Also turn off the old IP and connection link
        match.match_active = False
        match.match_provisioned = False
        match.match_creating = False
        #match.continuous_server_creating_timestamp = None
        match.match_destroying = True
        match.match_destroying_timestamp = datetime.datetime.now()
        match.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
        match.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
        match.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value
        matchController.update(match)

        ## update the match players also, so they are not stranded
        match_players = mpController.get_list_by_matchKeyId(match.key.id())
        for match_player in match_players:
            match_player.matchmakerPending = False
            match_player.matchmakerJoinPending = False
            match_player.matchmakerJoinable = False
            match_player.matchmakerCheckUnusedProcessed = True
            mpController.update(match_player)


        ## start a task to dealoocate the VM
        taskUrl='/task/matchmaker/vm/deallocate'
        name = "m%s" % match.key.id()
        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': match.continuous_server_project,
                                                                                "zone": match.continuous_server_zone,
                                                                                "name": name,
                                                                                "matchKeyId": match.key.id()
                                                                            }, countdown=2)


        ## create a server_instance record.

        destroying_datetime = datetime.datetime.now()
        total_seconds = (destroying_datetime - created_datetime).total_seconds()
        if total_seconds < VM_INSTANCE_MINIMUM_SECONDS:
            total_seconds = VM_INSTANCE_MINIMUM_SECONDS

        ## round up
        billable_min_uptime = int((total_seconds+(-total_seconds%60))//60)

        serverInstance = serverInstancesController.create(
            #serverKeyId = server.key.id(),
            #serverTitle = server.title,
            gameKeyId = match.gameKeyId,
            gameTitle = match.gameTitle,

            machine_type = match.continuous_server_machine_type,
            region_name = match.continuous_server_region,


            continuous_server_creating_timestamp = created_datetime,
            continuous_server_destroying_timestamp = destroying_datetime,

            uptime_minutes_billable = billable_min_uptime,

            #serverClusterKeyId = server.serverClusterKeyId,
            ##serverClusterTitle = server.serverClusterTitle,

            #userKeyId = server.userKeyId,
            processed = False,
            instanceType = 'match'
        )

        chat_channel = chatChannelController.get_by_channel_type_refKeyId('match', match.key.id())
        if chat_channel:
            ##  delete match chat if it still exists
            taskUrl='/task/chat/channel/delete'
            taskqueue.add(url=taskUrl, queue_name='chatChannelDelete', params={'key_id': chat_channel.key.id()}, countdown = 2,)
