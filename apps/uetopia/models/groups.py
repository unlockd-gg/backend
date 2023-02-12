import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## we need proto rpc definitions for event, player and games
#from apps.leet.models.group_events import *
#from apps.leet.models.group_games import *
#from apps.leet.models.group_player_members import *

class Groups(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    ownerPlayerKeyId = ndb.IntegerProperty()
    slugifyUrl = ndb.StringProperty()
    invisible = ndb.BooleanProperty() # hide this server from the group list
    iconServingUrl = ndb.StringProperty()
    bannerServingUrl = ndb.StringProperty()
    cssServingUrl = ndb.StringProperty()
    title = ndb.StringProperty()
    description = ndb.TextProperty()
    genre = ndb.StringProperty()
    website = ndb.StringProperty()
    tag = ndb.StringProperty()
    recruiting = ndb.BooleanProperty()
    recruiting_poilicy = ndb.StringProperty()
    application_message = ndb.StringProperty()

    currencyBalance = ndb.IntegerProperty(indexed=False) # how much does this group own - spendable or awardable

    ## Integrations
    slack_webhook = ndb.StringProperty(indexed=False)
    #slack_subscribe_vm_activity = ndb.BooleanProperty(indexed=False)
    slack_subscribe_errors = ndb.BooleanProperty(indexed=False)
    slack_subscribe_transactions = ndb.BooleanProperty(indexed=False)
    slack_subscribe_config_changes = ndb.BooleanProperty(indexed=False)
    slack_subscribe_new_users = ndb.BooleanProperty(indexed=False)
    slack_subscribe_tournaments = ndb.BooleanProperty(indexed=False)

    discord_webhook = ndb.StringProperty(indexed=False)
    #discord_subscribe_vm_activity = ndb.BooleanProperty(indexed=False)
    discord_subscribe_errors = ndb.BooleanProperty(indexed=False)
    discord_subscribe_transactions = ndb.BooleanProperty(indexed=False)
    discord_subscribe_config_changes = ndb.BooleanProperty(indexed=False)
    discord_subscribe_new_users = ndb.BooleanProperty(indexed=False)
    discord_subscribe_tournaments = ndb.BooleanProperty(indexed=False)
    discord_subscribe_group_event_feeds = ndb.BooleanProperty(indexed=False)
    discord_subscribe_game_event_feeds = ndb.BooleanProperty(indexed=False)
    discord_subscribe_consignments = ndb.BooleanProperty(indexed=False)

    #inGameTextureServingUrl = ndb.StringProperty()  ## this can be a general texture, but we should probably have this insdie group game instead.  TODO do it./

    def to_json(self):
        try:
            title = self.title.encode('utf-8')
        except:
            title = ''

        return ({
            u'key_id': str(self.key.id()),
            u'title': title,
            u'ownerPlayerKeyId': self.ownerPlayerKeyId,
            #u'slugifyUrl': self.slugifyUrl,
            u'invisible': self.invisible,
            u'iconServingUrl': self.iconServingUrl,
            u'bannerServingUrl': self.bannerServingUrl,
            u'cssServingUrl': self.cssServingUrl,
            u'description': self.description,
            u'genre': self.genre,
            u'website': self.website,
            u'tag': self.tag,
            u'recruiting': self.recruiting,
            u'recruiting_poilicy': self.recruiting_poilicy,
            u'application_message': self.application_message,
            #u'users':self.users,
            #u'games':self.games,
            #u'events':self.events,
        })


### PROTORPC MODELS FOR ENDPOINTS

class GroupCollectionPageRequest(messages.Message):
    """ a server's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

GROUP_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GroupCollectionPageRequest
)

class GroupGetRequest(messages.Message):
    """ a Group's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    application_message = messages.StringField(3)

GROUP_GET_RESOURCE = endpoints.ResourceContainer(
    GroupGetRequest
)

class GroupResponse(messages.Message):
    """ a groups's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    website = messages.StringField(4)
    genre = messages.StringField(5)
    invisible = messages.BooleanField(6)
    iconServingUrl = messages.StringField(7)
    bannerServingUrl  = messages.StringField(8)
    cssServingUrl = messages.StringField(9)
    tag = messages.StringField(10)
    recruiting = messages.BooleanField(11)
    recruiting_poilicy = messages.StringField(12)

    currencyBalance = messages.IntegerField(13, variant=messages.Variant.INT32)

    application_message = messages.StringField(14)

    slack_webhook = messages.StringField(101)
    slack_subscribe_errors = messages.BooleanField(103)
    slack_subscribe_transactions = messages.BooleanField(104)
    slack_subscribe_config_changes = messages.BooleanField(105)
    slack_subscribe_new_users = messages.BooleanField(106)
    slack_subscribe_tournaments = messages.BooleanField(107)

    discord_webhook = messages.StringField(207)
    discord_subscribe_errors = messages.BooleanField(209)
    discord_subscribe_transactions = messages.BooleanField(210)
    discord_subscribe_config_changes = messages.BooleanField(211)
    discord_subscribe_new_users = messages.BooleanField(212)
    discord_subscribe_tournaments = messages.BooleanField(213)

    discord_subscribe_group_event_feeds = messages.BooleanField(214)
    discord_subscribe_game_event_feeds = messages.BooleanField(215)
    discord_subscribe_consignments = messages.BooleanField(216)

    #inGameTextureServingUrl = messages.StringField(230)

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)
    #players = messages.MessageField(GroupMemberResponse, 14, repeated=True)
    #games = messages.MessageField(GroupGameResponse, 15, repeated=True)
    #events = messages.MessageField(GroupEventResponse, 16, repeated=True)


class GroupCreateRequest(messages.Message):
    """ create a Group """
    title = messages.StringField(1)
    description = messages.StringField(2)
    website = messages.StringField(3)
    genre = messages.StringField(4)
    invisible = messages.BooleanField(5)
    iconServingUrl = messages.StringField(6)
    bannerServingUrl  = messages.StringField(7)
    cssServingUrl = messages.StringField(8)
    tag = messages.StringField(9)
    recruiting = messages.BooleanField(10)
    recruiting_poilicy = messages.StringField(11)
    application_message = messages.StringField(14)


GROUP_CREATE_RESOURCE = endpoints.ResourceContainer(
    GroupCreateRequest
)

class GroupEditRequest(messages.Message):
    """ edit a group """

    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    website = messages.StringField(4)
    genre = messages.StringField(5)
    invisible = messages.BooleanField(6)
    iconServingUrl = messages.StringField(7)
    bannerServingUrl  = messages.StringField(8)
    cssServingUrl = messages.StringField(9)
    tag = messages.StringField(10)
    recruiting = messages.BooleanField(11)
    recruiting_poilicy = messages.StringField(12)

    application_message = messages.StringField(14)

    slack_webhook = messages.StringField(101)
    slack_subscribe_errors = messages.BooleanField(103)
    slack_subscribe_transactions = messages.BooleanField(104)
    slack_subscribe_config_changes = messages.BooleanField(105)
    slack_subscribe_new_users = messages.BooleanField(106)
    slack_subscribe_tournaments = messages.BooleanField(107)

    discord_webhook = messages.StringField(207)
    discord_subscribe_errors = messages.BooleanField(209)
    discord_subscribe_transactions = messages.BooleanField(210)
    discord_subscribe_config_changes = messages.BooleanField(211)
    discord_subscribe_new_users = messages.BooleanField(212)
    discord_subscribe_tournaments = messages.BooleanField(213)

    discord_subscribe_group_event_feeds = messages.BooleanField(214)
    discord_subscribe_game_event_feeds = messages.BooleanField(215)
    discord_subscribe_consignments = messages.BooleanField(216)

    #inGameTextureServingUrl = messages.StringField(230)


GROUP_EDIT_RESOURCE = endpoints.ResourceContainer(
    GroupEditRequest
)

class GroupCollection(messages.Message):
    """ multiple groups """
    groups = messages.MessageField(GroupResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    message = messages.StringField(6)
