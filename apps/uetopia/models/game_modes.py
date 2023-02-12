import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GameModes(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    onlineSubsystemReference = ndb.StringProperty()

    playersPerTeam = ndb.IntegerProperty(indexed=False)
    admissionFeePerPlayer = ndb.IntegerProperty(indexed=False)
    winRewardPerPlayer = ndb.IntegerProperty(indexed=False)
    teams = ndb.IntegerProperty(indexed=False)

    # which MM algo to use for this game mode
    # globalRank, regionalRank, globalScore, regionalScore, globalExperience, regionalExperience
    matchmakerAlgorithm = ndb.StringProperty(indexed=False)
    matchmakerDisparityMax = ndb.IntegerProperty(indexed=False)

    ads_allowed = ndb.BooleanProperty(indexed=False)
    ads_require_approval = ndb.BooleanProperty(indexed=False)
    ads_required = ndb.BooleanProperty(indexed=False)
    ads_default_textures =  ndb.StringProperty(indexed=False)
    ads_per_match_maximum = ndb.IntegerProperty(indexed=False) #how many billboards are in the game level
    ads_minimum_bid_per_impression = ndb.IntegerProperty(indexed=False) # minimum bid to advertize one time
    ads_description = ndb.StringProperty(indexed=False)

    ## metagame might want to enforce team sizes.
    teamSizeMin = ndb.IntegerProperty(indexed=False)
    teamSizeMax = ndb.IntegerProperty(indexed=False)

    ## require badges to play this game mode
    requireBadgeTags = ndb.StringProperty(repeated=True, indexed=False)

    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'playersPerTeam': self.playersPerTeam,
                u'admissionFeePerPlayer': self.admissionFeePerPlayer,
                u'winRewardPerPlayer':self.winRewardPerPlayer,
                u'teams': "%s" % self.teams,
                u'onlineSubsystemReference': "%s" % self.onlineSubsystemReference
        })

class GameModeResponse(messages.Message):
    """ a game mode's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(2)
    gameTitle = messages.StringField(3)
    onlineSubsystemReference = messages.StringField(4)
    playersPerTeam = messages.IntegerField(5, variant=messages.Variant.INT32)
    teams = messages.IntegerField(6, variant=messages.Variant.INT32)
    admissionFeePerPlayer = messages.IntegerField(7, variant=messages.Variant.INT32)
    winRewardPerPlayer = messages.IntegerField(8, variant=messages.Variant.INT32)

    matchmakerAlgorithm = messages.StringField(10)
    matchmakerDisparityMax = messages.IntegerField(11, variant=messages.Variant.INT32)

    ads_allowed = messages.BooleanField(12)
    ads_require_approval = messages.BooleanField(13)
    ads_required = messages.BooleanField(14)
    ads_default_textures =  messages.StringField(15)
    ads_per_match_maximum = messages.IntegerField(16, variant=messages.Variant.INT32)
    ads_minimum_bid_per_impression =messages.IntegerField(17, variant=messages.Variant.INT32)
    ads_description = messages.StringField(18)

    teamSizeMin = messages.IntegerField(19, variant=messages.Variant.INT32)
    teamSizeMax = messages.IntegerField(20, variant=messages.Variant.INT32)

    requireBadgeTags = messages.StringField(30, repeated=True)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameModeRequest(messages.Message):
    """ a game mode's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    gameKeyId = messages.IntegerField(2)
    gameTitle = messages.StringField(3)
    onlineSubsystemReference = messages.StringField(4)
    playersPerTeam = messages.IntegerField(5, variant=messages.Variant.INT32)
    teams = messages.IntegerField(6, variant=messages.Variant.INT32)
    admissionFeePerPlayer = messages.IntegerField(7, variant=messages.Variant.INT32)
    winRewardPerPlayer = messages.IntegerField(8, variant=messages.Variant.INT32)

    matchmakerAlgorithm = messages.StringField(10)
    matchmakerDisparityMax = messages.IntegerField(11, variant=messages.Variant.INT32)

    ads_allowed = messages.BooleanField(12)
    ads_require_approval = messages.BooleanField(13)
    ads_required = messages.BooleanField(14)
    ads_default_textures =  messages.StringField(15)
    ads_per_match_maximum = messages.IntegerField(16, variant=messages.Variant.INT32)
    ads_minimum_bid_per_impression =messages.IntegerField(17, variant=messages.Variant.INT32)
    ads_description = messages.StringField(18)

    teamSizeMin = messages.IntegerField(19, variant=messages.Variant.INT32)
    teamSizeMax = messages.IntegerField(20, variant=messages.Variant.INT32)

    requireBadgeTags = messages.StringField(30, repeated=True)

GAME_MODE_RESOURCE = endpoints.ResourceContainer(
    GameModeRequest
)


class GameModesCollection(messages.Message):
    """ multiple games """
    game_modes = messages.MessageField(GameModeResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameModesCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    groupGameKeyId = messages.IntegerField(5)

GAME_MODES_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GameModesCollectionPageRequest
)
