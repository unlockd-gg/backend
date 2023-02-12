import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

#from apps.leet.models.game_dedicated_status import *
#from apps.leet.models.match import *
#from apps.leet.models.game_player_members import *

class Games(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    # user owner
    googleUser = ndb.StringProperty()
    userKeyId = ndb.IntegerProperty()
    # general game info
    title = ndb.StringProperty()
    description = ndb.TextProperty(indexed=False)
    instructions = ndb.TextProperty(indexed=False)
    genre = ndb.StringProperty()
    website_url = ndb.StringProperty(indexed=False)
    icon_url = ndb.StringProperty(indexed=False)
    banner_url = ndb.StringProperty(indexed=False)
    css_url =  ndb.StringProperty(indexed=False)
    # OSS Party
    partySizeMaximum = ndb.IntegerProperty()
    # Visibility flags
    supported = ndb.BooleanProperty()
    invisible = ndb.BooleanProperty()
    invisible_developer_setting = ndb.BooleanProperty(indexed=True)  ## this invisible is controllable by the developer to allow developers to hide approved servers

    applied = ndb.BooleanProperty()
    application_date = ndb.DateTimeProperty(indexed=False)
    approved = ndb.BooleanProperty()
    approval_date = ndb.DateTimeProperty(indexed=False)
    approved_by = ndb.StringProperty(indexed=False)
    openToAllDevelopers = ndb.BooleanProperty()
    usersCanCreateServers = ndb.BooleanProperty(indexed=False)
    groupsCanCreateServers = ndb.BooleanProperty(indexed=False)
    # Server Specifications
    server_instace_match_deploy = ndb.BooleanProperty(indexed=False)  ## can servers handle one off matches
    server_instance_continuous = ndb.BooleanProperty(indexed=False) ## can servers handle continuous uptime with users constantly connecting and disconnecting
    tournaments_allowed = ndb.BooleanProperty(indexed=False)  ## are tournaments permitted
    vendors_allowed = ndb.BooleanProperty(indexed=False)  ## are vendors permitted

    ## moved to the vendor itself.  There are multiple types!!!
    #vendorDataTableId = ndb.IntegerProperty() ## When vendors expire, they need to be refunded as drops

    #matchmaker_player_minimum = ndb.IntegerProperty()
    #matchmaker_player_maximum = ndb.IntegerProperty()
    #matchmaker_promo_matches_enabled = ndb.BooleanProperty()

    ## API
    apiKey = ndb.StringProperty()
    apiSecret = ndb.StringProperty(indexed=False)

    ## Dynamic server creation
    match_deploy_vm = ndb.BooleanProperty(indexed=False)
    match_deploy_vm_preallocate = ndb.BooleanProperty(indexed=False)
    match_deploy_vm_preallocate_count = ndb.IntegerProperty(indexed=False)
    match_deploy_vm_cooldown_delay_seconds = ndb.IntegerProperty(indexed=False)

    match_deploy_vm_project = ndb.StringProperty(indexed=False)
    match_deploy_vm_bucket = ndb.StringProperty(indexed=False)
    #match_deploy_vm_region = ndb.StringProperty(indexed=True) # all regrions are supported.  user selectable.
    match_deploy_vm_source_disk_image = ndb.StringProperty(indexed=False)
    match_deploy_vm_machine_type = ndb.StringProperty(indexed=False)
    match_deploy_vm_startup_script_location = ndb.StringProperty(indexed=False)
    match_deploy_vm_shutdown_script_location = ndb.StringProperty(indexed=False)

    # match local testing ignores all VM stuff, and forces ip/api key /api secret
    match_deploy_vm_local_testing = ndb.BooleanProperty(indexed=False)
    match_deploy_vm_local_testing_connection_string = ndb.StringProperty(indexed=False)
    match_deploy_vm_local_APIKey = ndb.StringProperty(indexed=False)
    match_deploy_vm_local_APISecret = ndb.StringProperty(indexed=False)

    # metagame
    match_allow_metagame = ndb.BooleanProperty(indexed=False)
    match_metagame_api_url = ndb.StringProperty(indexed=False)

    # match auto-expire settings
    match_timeout_max_minutes = ndb.IntegerProperty(indexed=False)

    ## TODO move this into a separate game server deployment model
    server_instance_continuous_zone = ndb.StringProperty(indexed=False)
    server_instance_continuous_source_disk_image = ndb.StringProperty(indexed=False)
    server_instance_continuous_machine_type = ndb.StringProperty(indexed=False)
    server_instance_continuous_startup_script_location = ndb.StringProperty(indexed=False)

    ##Tournament
    #matchmaker_tournaments_enabled = ndb.BooleanProperty()

    ## This is all deprecated - part of game modes now.
    map_titles = ndb.StringProperty(repeated=True,indexed=False)
    map_ids = ndb.StringProperty(repeated=True,indexed=False)
    show_maps = ndb.BooleanProperty(indexed=False)

    player_configuration_titles = ndb.StringProperty(repeated=True, indexed=False)
    player_configuration_ids = ndb.StringProperty(repeated=True, indexed=False)
    show_number_of_players = ndb.BooleanProperty(indexed=False)

    #############################

    game_join_link_base = ndb.StringProperty(indexed=False)

    order = ndb.IntegerProperty()

    downloadable = ndb.BooleanProperty(indexed=False)
    download_url = ndb.StringProperty(indexed=False)

    trustable = ndb.BooleanProperty()

    currencyBalance = ndb.IntegerProperty(indexed=False) # how much does this game own - spendable or awardable

    characters_enabled = ndb.BooleanProperty(indexed=False)
    character_slots_new_user_default = ndb.IntegerProperty(indexed=False)

    ## Integrations
    slack_webhook = ndb.StringProperty(indexed=False)
    slack_subscribe_vm_activity = ndb.BooleanProperty(indexed=False)
    slack_subscribe_errors = ndb.BooleanProperty(indexed=False)
    slack_subscribe_transactions = ndb.BooleanProperty(indexed=False)
    slack_subscribe_config_changes = ndb.BooleanProperty(indexed=False)
    slack_subscribe_new_players = ndb.BooleanProperty(indexed=False)
    slack_subscribe_new_tournaments = ndb.BooleanProperty(indexed=False)
    slack_subscribe_tournament_rounds = ndb.BooleanProperty(indexed=False)


    discord_webhook_admin = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_subscribe_vm_activity = ndb.BooleanProperty(indexed=False)  # admin
    discord_subscribe_errors = ndb.BooleanProperty(indexed=False) # admin
    discord_subscribe_transactions = ndb.BooleanProperty(indexed=False) # admin
    discord_subscribe_config_changes = ndb.BooleanProperty(indexed=False) # admin
    discord_subscribe_new_players = ndb.BooleanProperty(indexed=False) # admin

    discord_webhook = ndb.StringProperty(indexed=False)  ## non-admin related feed
    discord_subscribe_new_tournaments = ndb.BooleanProperty(indexed=False) # non-admin
    discord_subscribe_tournament_rounds = ndb.BooleanProperty(indexed=False) # non-admin
    discord_subscribe_match_win = ndb.BooleanProperty(indexed=False) # non-admin

    ## Global matchmaker subscription flags
    discord_subscribe_matchmaker_task_status = ndb.BooleanProperty(indexed=False)
    discord_subscribe_server_manager_status = ndb.BooleanProperty(indexed=False)

    ## webhooks for each region
    discord_webhook_na_northeast1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_central1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_west1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_west2 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_west3 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_west4 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_east4 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_us_east1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_southamerica_east1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_europe_north1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_europe_west1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_europe_west2 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_europe_west3 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_europe_west4 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_europe_west6 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_south1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_southeast1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_east1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_east2 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_northeast1 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_northeast2 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_asia_northeast3 = ndb.StringProperty(indexed=False)  ## admin related feed
    discord_webhook_australia_southeast1 = ndb.StringProperty(indexed=False)  ## admin related feed

    group_custom_texture_instructions_link = ndb.StringProperty(indexed=False) ## link to instructions on how to set up custom group textures.
    group_custom_texture_default = ndb.StringProperty(indexed=False) ## default if the group does not have a texture set up.

    enforce_locks = ndb.BooleanProperty(indexed=False) ## default=FALSE.  Game Player lock is ignored.  Set to true for release games

    ## Support for patcher
    patcher_enabled = ndb.BooleanProperty(indexed=False)
    patcher_details_xml = ndb.TextProperty(indexed=False)


    ## Patch deployment page needs a delay in order to bring down all of the servers.
    ## Devs will enter the new patcher details, the new disk image, and the time to wait for servers to come down.
    ## matchmaker servers can just finish normally, but we need to check all long-running servers, send a warning chat, then shut them all down.
    patcher_patching = ndb.BooleanProperty(indexed=False) ## keep track of the patching state
    patcher_prepatch_xml = ndb.TextProperty(indexed=False) ## temporary storage for the patcher data.
    patcher_server_shutdown_seconds = ndb.IntegerProperty(indexed=False)
    patcher_server_shutdown_warning_chat = ndb.TextProperty(indexed=False)
    patcher_server_disk_image = ndb.StringProperty(indexed=False) ## temporarily keep track of the new disk image name



    def to_json(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'instructions':self.instructions,
                u'genre': "%s" % self.genre,
                u'icon_url': "%s" % self.icon_url,
                u'banner_url': self.banner_url,
                u'css_url': self.css_url,
                u'download_url': self.download_url,
                u'invisible_developer_setting': self.invisible_developer_setting,
                u'server_instace_match_deploy': self.server_instace_match_deploy,
                u'server_instance_continuous': self.server_instance_continuous,
                u'tournaments_allowed':self.tournaments_allowed,
                u'group_custom_texture_instructions_link':self.group_custom_texture_instructions_link,
                u'match_allow_metagame': self.match_allow_metagame,
                u'match_metagame_api_url':self.match_metagame_api_url

        })

    def to_json_with_modes(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'instructions':self.instructions,
                u'genre': "%s" % self.genre,
                u'icon_url': "%s" % self.icon_url,
                u'banner_url': self.banner_url,
                u'css_url': self.css_url,
                u'download_url': self.download_url,
                u'invisible_developer_setting': self.invisible_developer_setting or False,
                u'server_instace_match_deploy': self.server_instace_match_deploy,
                u'server_instance_continuous': self.server_instance_continuous,
                u'tournaments_allowed': self.tournaments_allowed,
                u'group_custom_texture_instructions_link':self.group_custom_texture_instructions_link,
                u'game_modes':self.game_modes,
                u'match_allow_metagame': self.match_allow_metagame,
                u'match_metagame_api_url':self.match_metagame_api_url
        })

    def to_json_with_modes_offers(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'instructions':self.instructions,
                u'genre': "%s" % self.genre,
                u'icon_url': "%s" % self.icon_url,
                u'banner_url': self.banner_url,
                u'css_url': self.css_url,
                u'download_url': self.download_url,
                u'website_url':self.website_url,
                u'invisible_developer_setting': self.invisible_developer_setting or False,
                u'server_instace_match_deploy': self.server_instace_match_deploy,
                u'server_instance_continuous': self.server_instance_continuous,
                u'tournaments_allowed': self.tournaments_allowed,
                u'group_custom_texture_instructions_link':self.group_custom_texture_instructions_link,
                u'game_modes':self.game_modes,
                u'match_allow_metagame': self.match_allow_metagame,
                u'match_metagame_api_url':self.match_metagame_api_url,
                u'offers': self.offers,
                u'characters_enabled': self.characters_enabled,
        })

    def to_json_for_patcher(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'icon_url': "%s" % self.icon_url,
                u'banner_url': self.banner_url,
                u'css_url': self.css_url,
                #u'patcher_details_xml': self.patcher_details_xml,

        })

### PROTORPC MODELS FOR ENDPOINTS

class GameCollectionPageRequest(messages.Message):
    """ a server's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

GAME_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GameCollectionPageRequest
)

class GameGetRequest(messages.Message):
    """ a game's key """
    key_id = messages.StringField(1)

GAME_GET_RESOURCE = endpoints.ResourceContainer(
    GameGetRequest
)


class GameCreateRequest(messages.Message):
    """ create a game """
    title = messages.StringField(1)
    description = messages.StringField(2)
    website_url = messages.StringField(3)
    genre = messages.StringField(4)
    server_instace_match_deploy = messages.BooleanField(6)
    server_instance_continuous = messages.BooleanField(7)


GAME_CREATE_RESOURCE = endpoints.ResourceContainer(
    GameCreateRequest
)

class GamesResponse(messages.Message):
    """ a game's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    genre = messages.StringField(4)
    message = messages.StringField(5)
    server_instace_match_deploy = messages.BooleanField(6) ## server_instace_match_deploy
    server_instance_continuous = messages.BooleanField(7)    ## server_instance_continuous
    instructions = messages.StringField(8)

    icon_url = messages.StringField(10)  ##  icon_url
    website_url = messages.StringField(11)    ## website_url
    userKeyId = messages.IntegerField(12, variant=messages.Variant.INT32)
    supported = messages.BooleanField(13)
    invisible = messages.BooleanField(14)
    invisible_developer_setting = messages.BooleanField(27)
    approved = messages.BooleanField(15)
    openToAllDevelopers = messages.BooleanField(16)
    banner_url = messages.StringField(17)
    css_url = messages.StringField(18)
    #matchmaker_player_minimum = messages.IntegerField(17)
    #matchmaker_player_maximum = messages.IntegerField(18)
    player_configuration_titles = messages.StringField(23, repeated=True)
    player_configuration_ids = messages.StringField(24, repeated=True)
    show_number_of_players = messages.BooleanField(25)
    game_join_link_base = messages.StringField(26)

    partySizeMaximum = messages.IntegerField(32, variant=messages.Variant.INT32)

    order = messages.IntegerField(33, variant=messages.Variant.INT32)

    apiKey = messages.StringField(34)
    apiSecret = messages.StringField(35)


    match_deploy_vm = messages.BooleanField(66)
    #match_deploy_vm_preallocate = messages.BooleanField(67)
    #match_deploy_vm_preallocate_count = messages.IntegerField(68, variant=messages.Variant.INT32)
    #match_deploy_vm_cooldown_delay_seconds = messages.IntegerField(69, variant=messages.Variant.INT32)

    match_deploy_vm_project = messages.StringField(70)
    match_deploy_vm_bucket = messages.StringField(71)
    #match_deploy_vm_region = ndb.StringProperty(indexed=True) # all regrions are supported.  user selectable.
    match_deploy_vm_source_disk_image = messages.StringField(72)
    match_deploy_vm_machine_type = messages.StringField(73)
    match_deploy_vm_startup_script_location = messages.StringField(74)
    match_deploy_vm_shutdown_script_location = messages.StringField(75)

    match_allow_metagame = messages.BooleanField(76)
    match_metagame_api_url = messages.StringField(77)

    match_timeout_max_minutes = messages.IntegerField(78, variant=messages.Variant.INT32)

    #matchmaker_dynamic_server_creation = messages.BooleanField(34)
    #matchmaker_tournaments_enabled = messages.BooleanField(35)
    #dynamic_server_zone = messages.StringField(36)
    #dynamic_server_source_disk_image = messages.StringField(37)
    #dynamic_server_machine_type = messages.StringField(38)
    #dynamic_server_startup_script_location = messages.StringField(39)
    #downloadable = messages.BooleanField(40)
    download_url = messages.StringField(41)
    #online_players = messages.MessageField(GameMemberResponse, 42, repeated=True)
    trustable = messages.BooleanField(43)

    usersCanCreateServers = messages.BooleanField(44)
    groupsCanCreateServers = messages.BooleanField(45)

    adminRequest = messages.BooleanField(54)
    developerRequest = messages.BooleanField(55)

    characters_enabled = messages.BooleanField(56)
    character_slots_new_user_default = messages.IntegerField(57, variant=messages.Variant.INT32)

    match_deploy_vm_local_testing = messages.BooleanField(91)
    match_deploy_vm_local_testing_connection_string = messages.StringField(92)
    match_deploy_vm_local_APIKey = messages.StringField(93)
    match_deploy_vm_local_APISecret = messages.StringField(94)

    slack_webhook = messages.StringField(101)
    slack_subscribe_vm_activity = messages.BooleanField(102)
    slack_subscribe_errors = messages.BooleanField(103)
    slack_subscribe_transactions = messages.BooleanField(104)
    slack_subscribe_config_changes = messages.BooleanField(105)
    slack_subscribe_new_players = messages.BooleanField(106)
    slack_subscribe_new_tournaments = messages.BooleanField(107)
    slack_subscribe_tournament_rounds = messages.BooleanField(108)

    discord_webhook = messages.StringField(207)
    discord_subscribe_vm_activity = messages.BooleanField(208)
    discord_subscribe_errors = messages.BooleanField(209)
    discord_subscribe_transactions = messages.BooleanField(210)
    discord_subscribe_config_changes = messages.BooleanField(211)
    discord_subscribe_new_players = messages.BooleanField(212)
    discord_subscribe_new_tournaments = messages.BooleanField(213)
    discord_subscribe_tournament_rounds = messages.BooleanField(214)
    discord_subscribe_match_win = messages.BooleanField(215)
    discord_webhook_admin = messages.StringField(220)

    discord_subscribe_matchmaker_task_status = messages.BooleanField(240)
    discord_subscribe_server_manager_status = messages.BooleanField(241)
    discord_webhook_na_northeast1 = messages.StringField(341)
    discord_webhook_us_central1 = messages.StringField(342)
    discord_webhook_us_west1 = messages.StringField(343)
    discord_webhook_us_west2 = messages.StringField(344)
    discord_webhook_us_west3 = messages.StringField(345)
    discord_webhook_us_west4 = messages.StringField(346)

    discord_webhook_us_east4 = messages.StringField(360)
    discord_webhook_us_east1 = messages.StringField(361)

    discord_webhook_southamerica_east1 = messages.StringField(370)

    discord_webhook_europe_north1 = messages.StringField(380)
    discord_webhook_europe_west1 = messages.StringField(381)
    discord_webhook_europe_west2 = messages.StringField(382)
    discord_webhook_europe_west3 = messages.StringField(383)
    discord_webhook_europe_west4 = messages.StringField(384)
    discord_webhook_europe_west6 = messages.StringField(385)

    discord_webhook_asia_south1 = messages.StringField(390)
    discord_webhook_asia_southeast1 = messages.StringField(391)
    discord_webhook_asia_east1 = messages.StringField(392)
    discord_webhook_asia_east2 = messages.StringField(393)

    discord_webhook_asia_northeast1 = messages.StringField(400)
    discord_webhook_asia_northeast2 = messages.StringField(401)
    discord_webhook_asia_northeast3 = messages.StringField(402)

    discord_webhook_australia_southeast1 = messages.StringField(410)

    ## tournament
    tournaments_allowed = messages.BooleanField(121)


    group_custom_texture_instructions_link = messages.StringField(122)
    group_custom_texture_default = messages.StringField(123)

    enforce_locks = messages.BooleanField(300)
    ## vendors - moved this to servers
    #vendors_allowed = messages.BooleanField(122)

    # moved to vendor itself.  There are multiple types!!!!
    #vendorDataTableId = messages.IntegerField(320, variant=messages.Variant.INT32)

    patcher_enabled = messages.BooleanField(310)
    patcher_details_xml = messages.StringField(311)

    patcher_patching = messages.BooleanField(330)
    patcher_prepatch_xml = messages.StringField(331)
    patcher_server_shutdown_seconds = messages.IntegerField(332, variant=messages.Variant.INT32)
    patcher_server_shutdown_warning_chat = messages.StringField(333)
    patcher_server_disk_image = messages.StringField(334)
    patcher_discord_message = messages.StringField(335)  ## This is only used to send the message from JS to discord.  It's not stored in the model itself.

    response_message = messages.StringField(440)
    response_successful = messages.BooleanField(450)

    ## also allow lookups from group game - TODO maybe move this request into a different resource container
    groupGameKeyId = messages.IntegerField(500, variant=messages.Variant.INT32)

GAMES_RESOURCE = endpoints.ResourceContainer(
    GamesResponse
)

class GamesCollection(messages.Message):
    """ multiple games """
    games = messages.MessageField(GamesResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GamesCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

GAMES_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GamesCollectionPageRequest
)


class GameDeveloperResponse(messages.Message):
    """ a game's data """
    key = messages.StringField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    genre = messages.StringField(4)
    websiteurl = messages.StringField(5)
    iconurl = messages.StringField(6)
    approved = messages.BooleanField(7)
    server_instace_match_deploy = messages.BooleanField(8)
    server_instance_continuous = messages.BooleanField(9)
    instructions = messages.StringField(10)
    message = messages.StringField(112)

class GameDeveloperCollection(messages.Message):
    """ multiple games """
    games = messages.MessageField(GameDeveloperResponse, 1, repeated=True)
    message = messages.StringField(2)
