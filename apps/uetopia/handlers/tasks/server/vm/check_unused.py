import logging
import re
import os
import datetime
import json
import uuid

from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.api import users
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.server_instances import ServerInstancesController
from apps.uetopia.controllers.server_links import ServerLinksController
from apps.uetopia.controllers.server_clusters import ServerClustersController
from apps.uetopia.controllers.server_shards import ServerShardsController

from configuration import *

class TaskCheckUnused(BaseHandler):
    """


    """
    def get(self):
        return self.post()

    def post(self):
        """

        """
        logging.info('TaskCheckUnused')

        spController = ServerPlayersController()
        serverController = ServersController()
        serverInstancesController = ServerInstancesController()
        serverLinksController = ServerLinksController()
        serverClusterController = ServerClustersController()
        serverShardController = ServerShardsController()

        matchKeyId = self.request.get('matchKeyId', None)
        serverKeyId = self.request.get('serverKeyId')

        if matchKeyId:
            logging.info('matchKeyId: ' + matchKeyId)

        ## TODO check to see if this server is part of an allocated server pool

        ## TODO check to see if the game has a specified pre-allocate amount

        ## TODO check to see if the game has a specific server cooldown

        ## check to see if there are any active players
        active_players = spController.get_list_active_by_server(int(serverKeyId))
        if len(active_players) > 0:
            logging.info('Found active players')
            ## start a task to check on the server - this is in the case that no users activate or deactivate.
            # muting this...  If there are active players, we don't need to make a new task, as the player disconnect should be sufficient.
            #taskUrl='/task/server/vm/checkunused'
            #taskqueue.add(url=taskUrl, queue_name='serverCheckUnused', params={"serverKeyId": serverKeyId
            #                                                                    }, countdown=CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_UNUSED_SECONDS)
            return

        server = serverController.get_by_key_id(int(serverKeyId))

        if not server:
            logging.info('Could not find the server - exiting')
            return

        ## prevent duplicate tasks
        if server.continuous_server_active == False:
            logging.info('continuous_server_active is false - exiting')
            return

        created_datetime = server.continuous_server_creating_timestamp


        ## Here we want to set the active flag to false so that the deallocation process knows that we are done with it.
        ## Also turn off the old IP and connection link
        server.continuous_server_active = False
        server.continuous_server_provisioned = False
        server.continuous_server_creating = False
        server.continuous_server_creating_timestamp = None
        server.continuous_server_destroying_timestamp = datetime.datetime.now()
        server.hostAddress = "None" ## using a string here because the ue json parser crashes if it's really a null value
        server.hostPort = "None" ## using a string here because the ue json parser crashes if it's really a null value
        server.hostConnectionLink = "None" ## using a string here because the ue json parser crashes if it's really a null value
        serverController.update(server)

        ## we need some special processing for instances and shards here
        if server.sharded_from_template:
            logging.info('this is a sharded server')
            ## set this server to offline in the server_shards

            ## check to see if there are any server shards currently online
            all_peer_server_shards = serverShardController.get_list_by_serverShardTemplateKeyId(server.sharded_from_template_serverKeyId)
            any_shard_online = False
            for peer_shard in all_peer_server_shards:
                if peer_shard.serverShardKeyId == server.key.id():
                    ## turn self to offline/0
                    peer_shard.online = False
                    peer_shard.playerCount = 0
                    serverShardController.update(peer_shard)

                else:
                    if peer_shard.online:
                        any_shard_online = True
            if not any_shard_online:
                logging.info('all shards offline')
                ##  remove hostConnectionLink from serverlinks
                target_server_links = serverLinksController.get_list_by_targetServerKeyId(server.sharded_from_template_serverKeyId)
                for link in target_server_links:
                    link.hostConnectionLink = "None"
                    link.targetStatusProvisioned = False
                    link.targetStatusOnline = False

                    serverLinksController.update(link)

        else:
            logging.info('not a sharded server')

            ##  remove hostConnectionLink from serverlinks
            target_server_links = serverLinksController.get_list_by_targetServerKeyId(server.key.id())
            for link in target_server_links:
                link.hostConnectionLink = "None"
                link.targetStatusProvisioned = False
                link.targetStatusOnline = False

                serverLinksController.update(link)

        ## get the server cluster so we can get the VM info
        server_cluster = serverClusterController.get_by_key_id(server.serverClusterKeyId)


        ## start a task to dealoocate the VM
        taskUrl='/task/server/vm/deallocate'
        taskqueue.add(url=taskUrl, queue_name='computeEngineOperations', params={'project': server_cluster.vm_project,
                                                                                "zone": server_cluster.vm_zone,
                                                                                "name": server.continuous_server_title,
                                                                                "serverKeyId": server.key.id()
                                                                            }, countdown=2)

        ## create a server_instance record.

        ## if this is a sharded or instanced server, use the parent server's ket/title
        if server.instanced_from_template:
            wallet_server_key_id = server.instanced_from_template_serverKeyId
            wallet_server_title = server.instanced_from_template_serverTitle
        elif server.sharded_from_template:
            wallet_server_key_id = server.sharded_from_template_serverKeyId
            wallet_server_title = server.sharded_from_template_serverTitle
        else:
            wallet_server_key_id = server.key.id()
            wallet_server_title = server.title

        destroying_datetime = datetime.datetime.now()
        total_seconds = (destroying_datetime - created_datetime).total_seconds()
        if total_seconds < VM_INSTANCE_MINIMUM_SECONDS:
            total_seconds = VM_INSTANCE_MINIMUM_SECONDS

        ## round up
        billable_min_uptime = int((total_seconds+(-total_seconds%60))//60)

        serverInstance = serverInstancesController.create(
            serverKeyId = wallet_server_key_id,
            serverTitle = wallet_server_title,

            machine_type = server_cluster.vm_machine_type,
            region_name = server_cluster.vm_region,

            continuous_server_creating_timestamp = created_datetime,
            continuous_server_destroying_timestamp = destroying_datetime,

            uptime_minutes_billable = billable_min_uptime,

            serverClusterKeyId = server.serverClusterKeyId,
            ##serverClusterTitle = server.serverClusterTitle,

            userKeyId = server.userKeyId,
            gameKeyId = server.gameKeyId,
            processed = False,
            instanceType = 'server'
        )
