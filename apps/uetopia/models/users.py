import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## grab game user members so we can send a list of shared games on user lookup
from apps.uetopia.models.game_players import *
## we want to send the sense data too
from apps.uetopia.models.sense import *
## and the match results user stuff
from apps.uetopia.models.match_results_user import *

class Users(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    # Google Auth
    googleUser = ndb.StringProperty()

    # Firebase auth
    firebaseUser = ndb.StringProperty()
    email = ndb.StringProperty()
    picture = ndb.StringProperty()
    sign_in_provider = ndb.StringProperty()
    refreshToken = ndb.StringProperty(indexed=False)

    # has the user submitted the profile form
    profile_saved = ndb.BooleanProperty()

    currencyBalance = ndb.IntegerProperty(indexed=False)

    # Registration stuff
    agreed_with_terms = ndb.BooleanProperty(indexed=True)
    age_verified = ndb.BooleanProperty(indexed=False)
    birthdate = ndb.DateTimeProperty(indexed=False)

    developer = ndb.BooleanProperty(indexed=False)
    ## Api stuff
    apiKey = ndb.StringProperty()
    apiSecret = ndb.StringProperty(indexed=False)

    admin = ndb.BooleanProperty(indexed=False)
    online = ndb.BooleanProperty()
    level = ndb.IntegerProperty(indexed=False)
    experience = ndb.IntegerProperty(indexed=False)
    playstyle_killer = ndb.IntegerProperty(indexed=False)
    playstyle_achiever = ndb.IntegerProperty(indexed=False)
    playstyle_explorer = ndb.IntegerProperty(indexed=False)
    playstyle_socializer = ndb.IntegerProperty(indexed=False)

    title_prefix = ndb.StringProperty(indexed=False)
    title_suffix = ndb.StringProperty(indexed=False)

    avatar_theme = ndb.StringProperty(indexed=False)

    groupTag = ndb.StringProperty(indexed=False)
    groupTagKeyId = ndb.IntegerProperty(indexed=False)

    defaultTeamTitle = ndb.StringProperty(indexed=False)

    ## Sense
    sense_initial_config_complete = ndb.BooleanProperty(indexed=False)
    sense_personality_complete = ndb.BooleanProperty(indexed=False)
    sense_personality = ndb.StringProperty(indexed=False)
    sense_platforms_complete = ndb.BooleanProperty(indexed=False)

    region = ndb.StringProperty(indexed=False)

    ## Geo information provided by appengine
    city = ndb.StringProperty(indexed=False)
    citylatlon = ndb.StringProperty(indexed=False)
    country = ndb.StringProperty(indexed=False)
    georegion = ndb.StringProperty(indexed=False)

    referral_processed = ndb.BooleanProperty(indexed=False)
    referred_by = ndb.IntegerProperty(indexed=False)

    ## game support preferences.
    ## Use this to control how we show user currency related information
    gsp_advertisements = ndb.BooleanProperty(indexed=False)
    gsp_totally_free = ndb.BooleanProperty(indexed=False)
    gsp_free_to_play = ndb.BooleanProperty(indexed=False)
    gsp_subscription = ndb.BooleanProperty(indexed=False)
    gsp_sticker_price_purchase = ndb.BooleanProperty(indexed=False)

    twitch_streamer = ndb.BooleanProperty(indexed=False)
    twitch_channel_id = ndb.StringProperty(indexed=False)
    twitch_currently_streaming = ndb.BooleanProperty(indexed=False)
    twitch_stream_game = ndb.StringProperty(indexed=False)
    twitch_stream_viewers = ndb.IntegerProperty(indexed=False)

    opt_out_email_promotions = ndb.BooleanProperty(indexed=False)
    opt_out_email_alerts = ndb.BooleanProperty(indexed=False)

    discord_webhook = ndb.StringProperty(indexed=False)
    discord_subscribe_errors = ndb.BooleanProperty(indexed=False)
    discord_subscribe_transactions = ndb.BooleanProperty(indexed=False)
    discord_subscribe_consignments = ndb.BooleanProperty(indexed=False)

    def to_json(self):
        return ({
            u'title': self.title,
            u'description': self.description,
            u'email': self.email,
            u'profile_saved': self.profile_saved,
            u'key': self.key.id(),
            u'admin': self.admin,
            u'developer': self.developer,
            u'region': self.region,
            u'online': self.online,
            u'level': self.level,
            u'playstyle_killer': self.playstyle_killer,
            u'playstyle_achiever': self.playstyle_achiever,
            u'playstyle_explorer': self.playstyle_explorer,
            u'playstyle_socializer': self.playstyle_socializer,
            u'title_prefix': self.title_prefix,
            u'title_suffix': self.title_suffix,
            u'avatar_theme': self.avatar_theme,
            u'currencyBalance':self.currencyBalance,
            u'agreed_with_terms':self.agreed_with_terms,
            u'gsp_advertisements':self.gsp_advertisements,
            u'gsp_totally_free':self.gsp_totally_free,
            u'gsp_free_to_play':self.gsp_free_to_play,
            u'gsp_subscription':self.gsp_subscription,
            u'gsp_sticker_price_purchase':self.gsp_sticker_price_purchase,
            u'twitch_streamer':  self.twitch_streamer,
            u'twitch_channel_id':  self.twitch_channel_id,
            u'twitch_currently_streaming':  self.twitch_currently_streaming,
            u'twitch_stream_game': self.twitch_stream_game,
            u'twitch_stream_viewers':self.twitch_stream_viewers,
            u'groupTagKeyIdStr':self.groupTagKeyId,
            u'groupTag': self.groupTag,
            u'opt_out_email_promotions': self.opt_out_email_promotions,
            u'opt_out_email_alerts': self.opt_out_email_alerts,
            u'defaultTeamTitle': self.defaultTeamTitle,

            u'discord_webhook': self.discord_webhook,
            u'discord_subscribe_errors': self.discord_subscribe_errors,
            u'discord_subscribe_transactions': self.discord_subscribe_transactions,
            u'discord_subscribe_consignments':self.discord_subscribe_consignments,

        })
    def to_json_public(self):
        return ({
            u'title': self.title,
            u'description': self.description,
            u'picture': self.picture,
            u'key_id': self.key.id(),
            u'region': self.region,
            u'online': self.online,
            u'level': self.level,
            u'playstyle_killer': self.playstyle_killer,
            u'playstyle_achiever': self.playstyle_achiever,
            u'playstyle_explorer': self.playstyle_explorer,
            u'playstyle_socializer': self.playstyle_socializer,
            u'title_prefix': self.title_prefix,
            u'title_suffix': self.title_suffix,
            u'avatar_theme': self.avatar_theme,
            u'twitch_streamer':  self.twitch_streamer,
            u'twitch_channel_id':  self.twitch_channel_id,
            u'twitch_currently_streaming':  self.twitch_currently_streaming,
            u'groupTagKeyIdStr':self.groupTagKeyId,
            u'groupTag': self.groupTag
        })



### PROTORPC MODELS FOR ENDPOINTS


class UserResponse(messages.Message):
    """ a user's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    currencyBalance = messages.IntegerField(3, variant=messages.Variant.INT32)
    description = messages.StringField(5)
    agreed_with_terms = messages.BooleanField(6)
    admin = messages.BooleanField(7)
    online = messages.BooleanField(8)
    level  = messages.IntegerField(9)
    experience = messages.IntegerField(10, variant=messages.Variant.INT32)
    playstyle_killer = messages.IntegerField(11, variant=messages.Variant.INT32)
    playstyle_achiever = messages.IntegerField(12, variant=messages.Variant.INT32)
    playstyle_explorer = messages.IntegerField(13, variant=messages.Variant.INT32)
    playstyle_socializer = messages.IntegerField(14, variant=messages.Variant.INT32)
    title_prefix = messages.StringField(15)
    title_suffix = messages.StringField(16)
    avatar_theme = messages.StringField(17)
    profile_saved = messages.BooleanField(18)
    developer = messages.BooleanField(19)
    apiKey = messages.StringField(20)
    apiSecret = messages.StringField(21)
    firebaseUser = messages.StringField(22)
    region = messages.StringField(23)
    email = messages.StringField(24)
    picture = messages.StringField(25)
    sign_in_provider = messages.StringField(26)
    accessToken = messages.StringField(27)

    opt_out_email_promotions = messages.BooleanField(31)
    opt_out_email_alerts = messages.BooleanField(32)

    defaultTeamTitle = messages.StringField(35)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)



class UserRequest(messages.Message):
    """ a users updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    avatar_theme = messages.StringField(3)
    description = messages.StringField(4)
    personality = messages.StringField(5)
    developer = messages.BooleanField(6)
    currencyBalance = messages.IntegerField(7, variant=messages.Variant.INT32)
    region = messages.StringField(8)
    email = messages.StringField(9)
    agreed_with_terms = messages.BooleanField(10)
    #googleUser = messages.StringField(22)
    gsp_advertisements = messages.BooleanField(21)
    gsp_totally_free = messages.BooleanField(22)
    gsp_free_to_play = messages.BooleanField(23)
    gsp_subscription = messages.BooleanField(24)
    gsp_sticker_price_purchase = messages.BooleanField(25)
    twitch_streamer = messages.BooleanField(26)
    twitch_channel_id = messages.StringField(27)

    opt_out_email_promotions = messages.BooleanField(31)
    opt_out_email_alerts = messages.BooleanField(32)

    defaultTeamTitle = messages.StringField(35)

    refreshToken = messages.StringField(81)
    gameKeyIdStr = messages.StringField(101)
    groupTagKeyIdStr = messages.StringField(102)

    discord_webhook = messages.StringField(120)
    discord_subscribe_errors = messages.BooleanField(121)
    discord_subscribe_transactions = messages.BooleanField(122)
    discord_subscribe_consignments = messages.BooleanField(123)

USER_RESOURCE = endpoints.ResourceContainer(
    UserRequest
)

class UserCollectionPageRequest(messages.Message):
    """ a server's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

USER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    UserCollectionPageRequest
)

class UserCollection(messages.Message):
    """ multiple Users """
    users = messages.MessageField(UserResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(7)
