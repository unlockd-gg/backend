import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

from apps.uetopia.models.vm_base import VMBase

## we need the definition of the server users member rpc message
from apps.uetopia.models.server_players import *
## and the leaderboard users
#from apps.uetopia.models.server_leaderboard_users import *
## and the server snapshots
#from apps.uetopia.models.server_snapshot import *

class Servers(VMBase):
    ## max active users
    maxActiveUsers = ndb.IntegerProperty(indexed=False)
    ## How many users are allowed to be authorized at any one time?
    maxAuthorizedUsers = ndb.IntegerProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()

    minimumCurrencyHold = ndb.IntegerProperty(indexed=False)
    totalCurrencyHeld = ndb.IntegerProperty(indexed=False)
    incrementCurrency = ndb.IntegerProperty(indexed=False)
    currencyAwarded = ndb.IntegerProperty(indexed=False) #how much has this server given to users
    serverCurrency = ndb.IntegerProperty(indexed=False) # how much does this server own - spendable or awardable

    serverAdminPaid = ndb.BooleanProperty(indexed=False) ## keep track of which servers require payouts
    disableAdminPayment = ndb.BooleanProperty(indexed=False) ## Disable Admin Payout as whole

    ## refresh server info instructs a gameserver that it should make a server_info call
    serverInfoRefreshNeeded = ndb.BooleanProperty(indexed=False)
    ## Hide the server from the server list
    invisible = ndb.BooleanProperty(indexed=True)
    invisible_developer_setting = ndb.BooleanProperty(indexed=True)  ## this invisible is controllable by the developer to allow developers to hide approved servers
    ## for use in server clusters.
    ## A common configuration would be to have a single entry point to a server cluster.

    ## *branded* server stuff
    ## Group Functionality
    groupServer = ndb.BooleanProperty(indexed=False)
    groupInvisible = ndb.BooleanProperty(indexed=False) # hide this server from the group list

    iconServingUrl = ndb.StringProperty(indexed=False)
    bannerServingUrl = ndb.StringProperty(indexed=False)
    cssServingUrl = ndb.StringProperty(indexed=False)

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)

    ## lastMapTitle may not be current. it is based on the most recent match results submission
    lastMapTitle = ndb.StringProperty(indexed=False)



    ## single user servers may have comporomised keys/secrets as they will be included in the codebase
    ## this prevents awards and kills from increasing a user's balance
    ## TODO implement the checks
    singleUserAdmissionOnly = ndb.BooleanProperty(indexed=False)

    ## continuous server creation - we could maybe combine these, but just for clarity we'll isolate them.
    continuous_server = ndb.BooleanProperty(indexed=False)
    continuous_server_creating = ndb.BooleanProperty(indexed=False)
    continuous_server_creating_timestamp = ndb.DateTimeProperty(indexed=False)
    continuous_server_provisioned = ndb.BooleanProperty(indexed=True)
    continuous_server_online = ndb.BooleanProperty(indexed=True)
    continuous_server_active = ndb.BooleanProperty(indexed=False)
    continuous_server_title = ndb.StringProperty(indexed=False)
    continuous_server_entry = ndb.BooleanProperty(indexed=True)
    continuous_server_destroying_timestamp = ndb.DateTimeProperty(indexed=False)


    ## server cluster membership
    serverClusterKeyId = ndb.IntegerProperty()

    ## Infinite server cluster support - TEMPLATE
    infinite_server_unused = ndb.BooleanProperty(indexed=False)
    gameLevelKeyId = ndb.IntegerProperty(indexed=False)
    gameLevelTitle = ndb.StringProperty(indexed=False)

    ## Instance support
    instance_server_template = ndb.BooleanProperty(indexed=False) ## this server is never used, it exists to clone out new instances

    ## delete the server completely after it has been used.
    ## Use True for instanced dungeons that should reset
    ## Use false for private dimensions or guild halls that should stay persistent
    instance_server_purge_after_use = ndb.BooleanProperty(indexed=False)

    ## how long to wait before purging the instance

    instance_server_purge_delay_seconds = ndb.IntegerProperty(indexed=False)
    instance_server_purge_scheduled_timestamp = ndb.DateTimeProperty(indexed=False)

    ## Config determines specific behavior and how joining is handled?
    ## user - only the user can enter (my vault)
    ## party - anyone in the party can enter (dungeon or raid)
    ## group - anyone in the group can enter (guild hall or dimension)
    instance_server_configuration = ndb.StringProperty(indexed=True)

    instance_party_size_maximum = ndb.IntegerProperty(indexed=False)

    ## SERVER INSTANCE SPECIFICS

    instanced_from_template = ndb.BooleanProperty(indexed=True)  ## this server is used, and was created from a instance template
    instanced_from_template_serverKeyId = ndb.IntegerProperty(indexed=True) ## which server template it was copied from
    instanced_from_template_serverTitle = ndb.StringProperty(indexed=False)

    instanced_server_completed = ndb.BooleanProperty(indexed=False)


    # instanced keys and titles

    instanced_for_userKeyId = ndb.IntegerProperty(indexed=True)
    instanced_for_userTitle = ndb.StringProperty(indexed=False)

    instanced_for_partyKeyId = ndb.IntegerProperty(indexed=True)
    instanced_for_partyTitle = ndb.StringProperty(indexed=False)

    instanced_for_groupKeyId = ndb.IntegerProperty(indexed=True)
    instanced_for_groupTitle = ndb.StringProperty(indexed=False)

    ## SHARDED SERVER SPECIFICS
    sharded_server_template = ndb.BooleanProperty(indexed=True) ## this server is never used, it exists to clone out new shards
    shard_count_maximum = ndb.IntegerProperty(indexed=False) ## how many shards are allowed
    sharded_player_capacity_threshold = ndb.IntegerProperty(indexed=False) ## at what point to stop accepting random (non-home shard) players
    sharded_player_capacity_maximum = ndb.IntegerProperty(indexed=False)

    sharded_from_template = ndb.BooleanProperty(indexed=True)  ## this server is used, and was created from a instance template
    sharded_from_template_serverKeyId = ndb.IntegerProperty(indexed=True) ## which server template it was copied from
    sharded_from_template_serverTitle = ndb.StringProperty(indexed=False)

    ## transaction thresholds

    server_to_game_transfer_threshold = ndb.IntegerProperty(indexed=False)
    server_to_game_transfer_exceeded = ndb.BooleanProperty(indexed=True)
    travelMode = ndb.StringProperty(indexed=False) # open, restricted

    randomRef = ndb.FloatProperty(indexed=True)

    ## vendors
    vendors_allowed = ndb.BooleanProperty(indexed=False)  ## are vendors permitted here
    player_created_vendors_allowed = ndb.BooleanProperty(indexed=False)  ## are player created vendors permitted here

    server_last_running_timestamp = ndb.DateTimeProperty(indexed=False)

    ## Custom server configuration settings, whioch can be changed inside the server itself
    configuration = ndb.TextProperty(indexed=False)

    drop_items_permitted = ndb.BooleanProperty(indexed=False)
    pickup_items_permitted = ndb.BooleanProperty(indexed=False)

    # require badge tags to play on this server
    requireBadgeTags = ndb.StringProperty(repeated=True, indexed=False)



    def to_json(self):
        try:
            title = self.title.encode('utf-8')
        except:
            title = ''

        try:
            active_player_count = self.active_player_count
        except:
            active_player_count = 0

        return ({
            u'key_id': str(self.key.id()),
            u'title': title,
            #u'incrementCurrency': self.incrementCurrency,
            u'minimumCurrencyHold': self.minimumCurrencyHold,
            u'admissionFee':self.admissionFee,
            u'continuous_server_creating':self.continuous_server_creating,
            u'continuous_server_provisioned':self.continuous_server_provisioned,
            u'continuous_server_region':self.continuous_server_region,
            u'active_player_count': active_player_count,
            u'instance_server_template': self.instance_server_template,
            u'sharded_server_template': self.sharded_server_template
        })

    def to_json_extended(self):
        try:
            active_player_count = self.active_player_count
        except:
            active_player_count = 0

        return ({
            u'key_id': str(self.key.id()),
            u'title': self.title,
            #u'incrementCurrency': self.incrementCurrency,
            u'minimumCurrencyHold': self.minimumCurrencyHold,
            u'admissionFee':self.admissionFee,
            u'serverCurrency':self.serverCurrency,
            u'bannerServingUrl':self.bannerServingUrl,

            #u'hostAddress': self.hostAddress,
            #u'hostPort': self.hostPort,
            #u'hostConnectionLink': self.hostConnectionLink,
            ## matchmaker dynamic server creation
            #u'match_server': self.match_server,
            #u'match_server_provisioned': self.match_server_provisioned,
            #u'match_server_active': self.match_server_active,
            #u'match_server_title': self.match_server_title,
            #u'match_server_zone': self.match_server_zone,

            ## continuous server creation - we could maybe combine these, but just for clarity we'll isolate them.
            u'continuous_server': self.continuous_server,
            u'continuous_server_creating': self.continuous_server_creating,
            u'continuous_server_provisioned': self.continuous_server_provisioned,
            u'continuous_server_active': self.continuous_server_active,
            u'continuous_server_title': self.continuous_server_title,
            u'continuous_server_entry': self.continuous_server_entry,
            u'continuous_server_zone': self.continuous_server_zone,
            u'active_player_count': active_player_count,
            u'instance_server_template': self.instance_server_template,
            u'sharded_server_template': self.sharded_server_template

        })




    def api_return_key(self):
        return ({
                u'key': self.key.urlsafe(),
                u'apiKey': self.apiKey,
                u'apiSecret': self.apiSecret
                })


    def to_json_for_session(self):
        try:
            title = self.title.encode('utf-8')
        except:
            title = ''
        return ({
            u'key': str(self.key.id()),
            u'title': title,
            u'session_host_address': self.hostConnectionLink,
            u'session_id': self.session_id,
            u'incrementCurrency': self.incrementCurrency,
            u'minimumCurrencyHold': self.minimumCurrencyHold,
            #u'stakesClass':self.stakesClass,
            u'admissionFee':self.admissionFee,
        })

### PROTORPC MODELS FOR ENDPOINTS

class ServerCollectionPageRequest(messages.Message):
    """ a server's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    serverClusterKeyId = messages.IntegerField(17)
    serverClusterKeyIdStr = messages.StringField(18)  ## engine clients will be sending a string
    gameKeyId = messages.IntegerField(19)
    sharded_from_template_serverKeyId = messages.IntegerField(20)
    instanced_from_template_serverKeyId = messages.IntegerField(21)


SERVER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    ServerCollectionPageRequest
)

class ServerGetRequest(messages.Message):
    """ a server's data """
    key_id = messages.IntegerField(1)

SERVER_GET_RESOURCE = endpoints.ResourceContainer(
    ServerGetRequest
)

class ServerAuthorizeRequest(messages.Message):
    """ a server's data """
    key_id = messages.StringField(1)
    currencyHold = messages.IntegerField(2)

SERVER_AUTHORIZE_RESOURCE = endpoints.ResourceContainer(
    ServerAuthorizeRequest
)

class ServerCreateRequest(messages.Message):
    """ a server's data """
    title = messages.StringField(1)
    hostAddress = messages.StringField(2)
    hostPort = messages.StringField(3)
    hostConnectionLink = messages.StringField(4)
    gameKeyId = messages.IntegerField(5)
    maxActiveUsers = messages.IntegerField(6)
    maxAuthorizedUsers = messages.IntegerField(7)
    minimumCurrencyHold = messages.IntegerField(8)
    incrementCurrency = messages.IntegerField(9)
    admissionFee = messages.IntegerField(18)
    serverClusterKeyId = messages.IntegerField(19)
    description = messages.StringField(20)
    gameLevelKeyId = messages.IntegerField(21, variant=messages.Variant.INT32)
    infinite_server_unused = messages.BooleanField(22)
    invisible_developer_setting = messages.BooleanField(30)
    session_host_address = messages.StringField(62)
    session_id = messages.StringField(63)
    requireBadgeTags = messages.StringField(70, repeated=True)


SERVER_CREATE_RESOURCE = endpoints.ResourceContainer(
    ServerCreateRequest
)

class ServerEditRequest(messages.Message):
    """ a server's data.  Only an Admin or developer can submit this.  """
    title = messages.StringField(1)
    description = messages.StringField(2)
    hostAddress = messages.StringField(3)
    hostPort = messages.StringField(4)
    hostConnectionLink = messages.StringField(5)
    gameKeyId = messages.IntegerField(6)

    maxActiveUsers = messages.IntegerField(7)
    maxAuthorizedUsers = messages.IntegerField(8)
    minimumCurrencyHold = messages.IntegerField(9)

    incrementCurrency = messages.IntegerField(10)

    key_id = messages.IntegerField(19)

    iconServingUrl = messages.StringField(20)
    bannerServingUrl = messages.StringField(21)
    cssServingUrl = messages.StringField(22)

    ###########################
    #### admin only fields ####
    ###########################

    userKeyId = messages.IntegerField(123)
    gameTitle = messages.StringField(126)

    disableAdminPayment = messages.BooleanField(129)
    invisible = messages.BooleanField(131)

    groupServer = messages.BooleanField(133)
    groupInvisible = messages.BooleanField(134)

    groupKeyId = messages.IntegerField(135)
    groupTitle = messages.StringField(136)

    ## admin or owner fields

    continuous_server = messages.BooleanField(43)


    #continuous_server_bucket = messages.StringField(44)
    #continuous_server_region = messages.StringField(45)
    #continuous_server_zone = messages.StringField(46)
    #continuous_server_source_disk_image = messages.StringField(47)
    #continuous_server_machine_type = messages.StringField(48)
    #continuous_server_startup_script_location = messages.StringField(49)
    #continuous_server_shutdown_script_location = messages.StringField(50)
    continuous_server_entry = messages.BooleanField(51)
    continuous_server_provisioned = messages.BooleanField(52)

    invisible_developer_setting = messages.BooleanField(53)
    admissionFee = messages.IntegerField(54)
    #continuous_server_project = messages.StringField(55)

    gameLevelKeyId = messages.IntegerField(56, variant=messages.Variant.INT32)
    infinite_server_unused = messages.BooleanField(57)

    adminRequest = messages.BooleanField(74)
    developerRequest = messages.BooleanField(75)

    session_host_address = messages.StringField(62)
    session_id = messages.StringField(63)

    server_to_game_transfer_threshold = messages.IntegerField(70, variant=messages.Variant.INT32)

    randomRef = messages.FloatField(71)

    instance_server_template = messages.BooleanField(100)
    instance_server_purge_after_use = messages.BooleanField(101)
    instance_server_purge_delay_seconds = messages.IntegerField(102, variant=messages.Variant.INT32)
    instance_server_configuration = messages.StringField(103)
    instance_party_size_maximum = messages.IntegerField(104, variant=messages.Variant.INT32)

    sharded_server_template = messages.BooleanField(111)
    shard_count_maximum = messages.IntegerField(112, variant=messages.Variant.INT32)
    sharded_player_capacity_threshold = messages.IntegerField(113, variant=messages.Variant.INT32)
    sharded_player_capacity_maximum = messages.IntegerField(114, variant=messages.Variant.INT32)

    vendors_allowed = messages.BooleanField(151)
    player_created_vendors_allowed = messages.BooleanField(152)

    configuration = messages.StringField(160)

    drop_items_permitted = messages.BooleanField(171)
    pickup_items_permitted = messages.BooleanField(172)

    requireBadgeTags = messages.StringField(173, repeated=True)


SERVER_EDIT_RESOURCE = endpoints.ResourceContainer(
    ServerEditRequest
)

class ServerDeveloperResponse(messages.Message):
    """ a server's data """

    key_id = messages.IntegerField(1)

    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(5)
    incrementCurrency = messages.IntegerField(6)
    minimumCurrencyHold = messages.IntegerField(7)
    currencyAwarded = messages.IntegerField(8)
    iconServingUrl = messages.StringField(11)
    bannerServingUrl = messages.StringField(12)
    cssServingUrl = messages.StringField(13)
    lastMapTitle = messages.StringField(17)
    admissionFee = messages.IntegerField(18)
    users = messages.StringField(19)  ## not sure what we have to do here to prepare angular to deal with the users array.  sending a string for now

    hostAddress = messages.StringField(20)
    hostPort = messages.StringField(21)
    hostConnectionLink = messages.StringField(22)

    apiKey = messages.StringField(25)
    apiSecret = messages.StringField(26)
    #errors = messages.StringField(27)
    authorization = messages.BooleanField(28)
    #message = messages.StringField(29)
    gameLevelKeyId = messages.IntegerField(29, variant=messages.Variant.INT32)
    infinite_server_unused = messages.BooleanField(30)

    invisible_developer_setting = messages.BooleanField(50)

    server_to_game_transfer_threshold = messages.IntegerField(70, variant=messages.Variant.INT32)

    randomRef = messages.FloatField(71)

    instance_server_template = messages.BooleanField(100)
    instance_server_purge_after_use = messages.BooleanField(101)
    instance_server_purge_delay_seconds = messages.IntegerField(102, variant=messages.Variant.INT32)
    instance_server_configuration = messages.StringField(103)
    instance_party_size_maximum = messages.IntegerField(104, variant=messages.Variant.INT32)
    instanced_from_template = messages.BooleanField(105)

    instanced_for_userKeyId = messages.IntegerField(206, variant=messages.Variant.INT32)
    instanced_for_userTitle = messages.StringField(207)
    instanced_for_partyKeyId = messages.IntegerField(208, variant=messages.Variant.INT32)
    instanced_for_partyTitle = messages.StringField(209)
    instanced_for_groupKeyId = messages.IntegerField(210, variant=messages.Variant.INT32)
    instanced_for_groupTitle = messages.StringField(211)

    sharded_server_template = messages.BooleanField(111)
    shard_count_maximum = messages.IntegerField(112, variant=messages.Variant.INT32)
    sharded_player_capacity_threshold = messages.IntegerField(113, variant=messages.Variant.INT32)
    sharded_player_capacity_maximum = messages.IntegerField(114, variant=messages.Variant.INT32)
    sharded_from_template = messages.BooleanField(115)

    response_message = messages.StringField(140)
    response_successful = messages.BooleanField(150)

    vendors_allowed = messages.BooleanField(151)
    player_created_vendors_allowed = messages.BooleanField(152)

    configuration = messages.StringField(160)

    drop_items_permitted = messages.BooleanField(171)
    pickup_items_permitted = messages.BooleanField(172)

    requireBadgeTags = messages.StringField(173, repeated=True)

class ServerResponse(messages.Message):
    """ a server's data """
    key_id = messages.IntegerField(1)

    title = messages.StringField(2)
    description = messages.StringField(3)
    hostAddress = messages.StringField(4)
    hostPort = messages.StringField(5)
    hostConnectionLink = messages.StringField(6)

    gameKeyId = messages.IntegerField(7)
    gameTitle = messages.StringField(8)
    maxActiveUsers = messages.IntegerField(9, variant=messages.Variant.INT32)
    maxAuthorizedUsers = messages.IntegerField(10, variant=messages.Variant.INT32)

    incrementCurrency = messages.IntegerField(11, variant=messages.Variant.INT32)
    minimumCurrencyHold = messages.IntegerField(12, variant=messages.Variant.INT32)

    serverAdminUserKey = messages.StringField(14)
    stakesClass = messages.StringField(16)
    admissionFee = messages.IntegerField(20, variant=messages.Variant.INT32)

    iconServingUrl = messages.StringField(21)
    bannerServingUrl = messages.StringField(22)
    cssServingUrl = messages.StringField(23)

    apiKey = messages.StringField(24)
    apiSecret = messages.StringField(25)

    userKeyId = messages.IntegerField(26)

    disableAdminPayment = messages.BooleanField(30)
    invisible = messages.BooleanField(32)
    groupServer = messages.BooleanField(34)
    groupInvisible = messages.BooleanField(35)
    groupKeyId = messages.IntegerField(36)
    groupTitle = messages.StringField(37)

    users = messages.MessageField(ServerPlayerBasicResponse, 45, repeated=True)

    lastMapTitle = messages.StringField(46)

    admissionFee = messages.IntegerField(47, variant=messages.Variant.INT32)
    currencyAwarded = messages.IntegerField(49, variant=messages.Variant.INT32)

    continuous_server = messages.BooleanField(50)

    continuous_server_provisioned = messages.BooleanField(51)
    continuous_server_active = messages.BooleanField(52)

    ### deprecated - use server cluster
    continuous_server_bucket = messages.StringField(53)
    continuous_server_zone = messages.StringField(54)
    continuous_server_region = messages.StringField(55)

    continuous_server_source_disk_image = messages.StringField(56)
    continuous_server_machine_type = messages.StringField(57)
    continuous_server_startup_script_location = messages.StringField(58)
    continuous_server_shutdown_script_location = messages.StringField(59)
    continuous_server_project = messages.StringField(60)
    ##########################

    continuous_server_entry = messages.BooleanField(61)

    invisible_developer_setting = messages.BooleanField(62)
    serverClusterKeyId = messages.IntegerField(63)

    session_host_address = messages.StringField(64)
    session_id = messages.StringField(65)

    gameLevelKeyId = messages.IntegerField(66, variant=messages.Variant.INT32)
    infinite_server_unused = messages.BooleanField(67)

    server_to_game_transfer_threshold = messages.IntegerField(70, variant=messages.Variant.INT32)

    randomRef = messages.FloatField(71)

    instance_server_template = messages.BooleanField(100)
    instance_server_purge_after_use = messages.BooleanField(101)
    instance_server_purge_delay_seconds = messages.IntegerField(102, variant=messages.Variant.INT32)
    instance_server_configuration = messages.StringField(103)
    instance_party_size_maximum = messages.IntegerField(104, variant=messages.Variant.INT32)
    instanced_from_template = messages.BooleanField(105)

    instanced_for_userKeyId = messages.IntegerField(206, variant=messages.Variant.INT32)
    instanced_for_userTitle = messages.StringField(207)
    instanced_for_partyKeyId = messages.IntegerField(208, variant=messages.Variant.INT32)
    instanced_for_partyTitle = messages.StringField(209)
    instanced_for_groupKeyId = messages.IntegerField(210, variant=messages.Variant.INT32)
    instanced_for_groupTitle = messages.StringField(211)

    sharded_server_template = messages.BooleanField(111)
    shard_count_maximum = messages.IntegerField(112, variant=messages.Variant.INT32)
    sharded_player_capacity_threshold = messages.IntegerField(113, variant=messages.Variant.INT32)
    sharded_player_capacity_maximum = messages.IntegerField(114, variant=messages.Variant.INT32)
    sharded_from_template = messages.BooleanField(115)

    vendors_allowed = messages.BooleanField(151)
    player_created_vendors_allowed = messages.BooleanField(152)

    configuration = messages.StringField(160)

    drop_items_permitted = messages.BooleanField(171)
    pickup_items_permitted = messages.BooleanField(172)

    requireBadgeTags = messages.StringField(173, repeated=True)

    key_id_str = messages.StringField(950) ## engine clients need strings still?
    response_message = messages.StringField(970)
    response_successful = messages.BooleanField(980)




class ServerCollection(messages.Message):
    """ multiple servers """
    servers = messages.MessageField(ServerResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(70)
    response_successful = messages.BooleanField(80)

class ServerDeveloperCollection(messages.Message):
    """ multiple servers """
    servers = messages.MessageField(ServerDeveloperResponse, 1, repeated=True)
    message = messages.StringField(2)

class ServerAuthorizeResponse(messages.Message):
    """ a server's basic data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    response_message = messages.StringField(70)
    response_successful = messages.BooleanField(80)
