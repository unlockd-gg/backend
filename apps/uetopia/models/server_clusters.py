import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class ServerClusters(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)
    max_count = ndb.IntegerProperty(indexed=False)
    min_online = ndb.IntegerProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()

    groupCluster = ndb.BooleanProperty(indexed=False)
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)

    serverCreationMode = ndb.StringProperty(indexed=False) # limited, infinite
    server_to_game_transfer_threshold = ndb.IntegerProperty(indexed=False) # when a server gets above this threshold, send the cred to the game
    game_to_server_initial_transfer_amount = ndb.IntegerProperty(indexed=False) # when a new server is created, send the cred from the game
    travelMode = ndb.StringProperty(indexed=False) # free, restricted
    newPlayerStartMode = ndb.StringProperty(indexed=False) # random entry, personal server
    rejoiningPlayerStartMode = ndb.StringProperty(indexed=False) #previous, random entry, personal server

    # moved from VMbase - we need an easier way to change VM server settings in bulk
    vm_project = ndb.StringProperty(indexed=False)
    vm_bucket = ndb.StringProperty(indexed=False)
    vm_region = ndb.StringProperty(indexed=True)
    vm_zone = ndb.StringProperty(indexed=False)
    vm_disk_image = ndb.StringProperty(indexed=False)
    vm_machine_type = ndb.StringProperty(indexed=False)
    vm_startup_script_location = ndb.StringProperty(indexed=False)
    vm_shutdown_script_location = ndb.StringProperty(indexed=False)

    server_manager_task_running = ndb.BooleanProperty(indexed=False)
    server_manager_task_should_stop = ndb.BooleanProperty(indexed=False)

    accept_matchmaker_events_for_this_region = ndb.BooleanProperty(indexed=True)

    def to_json(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'region':self.vm_region
        })

class ServerClusterGetRequest(messages.Message):
    """ a match's key """
    aekey = messages.StringField(1)

SERVER_CLUSTER_GET_RESOURCE = endpoints.ResourceContainer(
    ServerClusterGetRequest
)

class ServerClusterCreateRequest(messages.Message):
    """ a ServerCluster """
    title = messages.StringField(1)
    description = messages.StringField(2)
    max_count = messages.IntegerField(3, variant=messages.Variant.INT32)
    min_online = messages.IntegerField(4, variant=messages.Variant.INT32)

    gameKeyId = messages.IntegerField(5)

    groupCluster = messages.BooleanField(6)
    groupKeyId = messages.IntegerField(7)
    groupTitle = messages.StringField(8)

    userKeyId = messages.IntegerField(9)
    userTitle = messages.StringField(10)

    serverCreationMode = messages.StringField(21)
    server_to_game_transfer_threshold = messages.IntegerField(22, variant=messages.Variant.INT32)
    game_to_server_initial_transfer_amount = messages.IntegerField(23, variant=messages.Variant.INT32)
    travelMode = messages.StringField(24)
    newPlayerStartMode = messages.StringField(25)
    rejoiningPlayerStartMode = messages.StringField(26)

    server_manager_task = messages.BooleanField(27)

    response_message = messages.StringField(41)
    response_successful = messages.BooleanField(50)


SERVER_CLUSTER_CREATE_RESOURCE = endpoints.ResourceContainer(
    ServerClusterCreateRequest
)

class ServerClusterEditRequest(messages.Message):
    """ a ServerCluster's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    max_count = messages.IntegerField(4, variant=messages.Variant.INT32)
    min_online = messages.IntegerField(5, variant=messages.Variant.INT32)

    gameKeyId = messages.IntegerField(6)

    groupCluster = messages.BooleanField(7)
    groupKeyId = messages.IntegerField(8)
    groupTitle = messages.StringField(9)

    userKeyId = messages.IntegerField(10)
    userTitle = messages.StringField(11)

    serverCreationMode = messages.StringField(21)
    server_to_game_transfer_threshold = messages.IntegerField(22, variant=messages.Variant.INT32)
    game_to_server_initial_transfer_amount = messages.IntegerField(23, variant=messages.Variant.INT32)
    travelMode = messages.StringField(24)
    newPlayerStartMode = messages.StringField(25)
    rejoiningPlayerStartMode = messages.StringField(26)

    server_manager_task = messages.BooleanField(27)

    vm_project = messages.StringField(61)
    vm_bucket = messages.StringField(62)
    vm_region = messages.StringField(63)
    vm_zone = messages.StringField(64)
    vm_disk_image = messages.StringField(65)
    vm_machine_type = messages.StringField(66)
    vm_startup_script_location = messages.StringField(67)
    vm_shutdown_script_location = messages.StringField(68)

    accept_matchmaker_events_for_this_region = messages.BooleanField(70)


SERVER_CLUSTER_EDIT_RESOURCE = endpoints.ResourceContainer(
    ServerClusterEditRequest
)

class ServerClusterResponse(messages.Message):
    """ a ServerCluster's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    max_count = messages.IntegerField(4, variant=messages.Variant.INT32)
    min_online = messages.IntegerField(5, variant=messages.Variant.INT32)

    gameKeyId = messages.IntegerField(6)

    groupCluster = messages.BooleanField(7)
    groupKeyId = messages.IntegerField(8)
    groupTitle = messages.StringField(9)

    userKeyId = messages.IntegerField(10)
    userTitle = messages.StringField(11)

    serverCreationMode = messages.StringField(21)
    server_to_game_transfer_threshold = messages.IntegerField(22, variant=messages.Variant.INT32)
    game_to_server_initial_transfer_amount = messages.IntegerField(23, variant=messages.Variant.INT32)
    travelMode = messages.StringField(24)
    newPlayerStartMode = messages.StringField(25)
    rejoiningPlayerStartMode = messages.StringField(26)

    server_manager_task = messages.BooleanField(27)

    vm_project = messages.StringField(61)
    vm_bucket = messages.StringField(62)
    vm_region = messages.StringField(63)
    vm_zone = messages.StringField(64)
    vm_disk_image = messages.StringField(65)
    vm_machine_type = messages.StringField(66)
    vm_startup_script_location = messages.StringField(67)
    vm_shutdown_script_location = messages.StringField(68)

    accept_matchmaker_events_for_this_region = messages.BooleanField(70)

    key_id_str = messages.StringField(950) ## engine clients need strings still?
    response_message = messages.StringField(112)
    response_successful = messages.BooleanField(150)


class ServerClusterResponseCollectionPageRequest(messages.Message):
    """ a server's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(6)
    gameKeyIdStr = messages.StringField(7) ## UE clients send id as string

SERVER_CLUSTER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    ServerClusterResponseCollectionPageRequest
)

class ServerClusterCollection(messages.Message):
    """ multiple ServerClusters """
    server_clusters = messages.MessageField(ServerClusterResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
