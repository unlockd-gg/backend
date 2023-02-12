import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GameLevels(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    title = ndb.StringProperty(indexed=False)
    engineTravelUrlString= ndb.StringProperty(indexed=False)
    selectionProbability = ndb.IntegerProperty(indexed=False)

    outgoingLinkMin = ndb.IntegerProperty(indexed=False) ## the minimum number of new servers to create
    outgoingLinkMax = ndb.IntegerProperty(indexed=False) ## the maximum number of new servers to create

    chanceToCreateReturnLink = ndb.FloatProperty(indexed=False) # 1.0 will always create a link back to the server that spawned it
    chanceToCreateRandomLink = ndb.FloatProperty(indexed=False) # 1.0 will always create a link to a random existing server
    randomLinkLevelTraverse = ndb.IntegerProperty(indexed=False) # how many link levels to traverse to find an existing link (should be 1 or 2 only )

    minimumCurrencyHold = ndb.IntegerProperty(indexed=False)

    ## This needs shard info - to support sharding on infinite mode.
    ## SHARDED SERVER SPECIFICS
    sharded_server_template = ndb.BooleanProperty(indexed=False) ## this server exists to clone out new shards
    shard_count_maximum = ndb.IntegerProperty(indexed=False) ## how many shards are allowed
    sharded_player_capacity_threshold = ndb.IntegerProperty(indexed=False) ## at what point to stop accepting random (non-home shard) players
    sharded_player_capacity_maximum = ndb.IntegerProperty(indexed=False)

    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title
        })

class GameLevelResponse(messages.Message):
    """ a game level's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(3)
    title = messages.StringField(4)
    engineTravelUrlString = messages.StringField(5)
    selectionProbability = messages.IntegerField(6, variant=messages.Variant.INT32)
    outgoingLinkMin = messages.IntegerField(7, variant=messages.Variant.INT32)
    outgoingLinkMax = messages.IntegerField(8, variant=messages.Variant.INT32)

    chanceToCreateReturnLink = messages.FloatField(12)
    chanceToCreateRandomLink = messages.FloatField(13)
    randomLinkLevelTraverse = messages.IntegerField(14, variant=messages.Variant.INT32)

    minimumCurrencyHold = messages.IntegerField(15, variant=messages.Variant.INT32)

    sharded_server_template = messages.BooleanField(21)
    shard_count_maximum = messages.IntegerField(22, variant=messages.Variant.INT32)
    sharded_player_capacity_threshold = messages.IntegerField(23, variant=messages.Variant.INT32)
    sharded_player_capacity_maximum = messages.IntegerField(24, variant=messages.Variant.INT32)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameLevelRequest(messages.Message):
    """ a game level's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(3)
    title = messages.StringField(4)
    engineTravelUrlString = messages.StringField(5)
    selectionProbability = messages.IntegerField(6, variant=messages.Variant.INT32)
    outgoingLinkMin = messages.IntegerField(7, variant=messages.Variant.INT32)
    outgoingLinkMax = messages.IntegerField(8, variant=messages.Variant.INT32)

    chanceToCreateReturnLink = messages.FloatField(12)
    chanceToCreateRandomLink = messages.FloatField(13)
    randomLinkLevelTraverse = messages.IntegerField(14, variant=messages.Variant.INT32)

    minimumCurrencyHold = messages.IntegerField(15, variant=messages.Variant.INT32)

    sharded_server_template = messages.BooleanField(21)
    shard_count_maximum = messages.IntegerField(22, variant=messages.Variant.INT32)
    sharded_player_capacity_threshold = messages.IntegerField(23, variant=messages.Variant.INT32)
    sharded_player_capacity_maximum = messages.IntegerField(24, variant=messages.Variant.INT32)


GAME_LEVEL_RESOURCE = endpoints.ResourceContainer(
    GameLevelRequest
)


class GameLevelsCollection(messages.Message):
    """ multiple games """
    game_levels = messages.MessageField(GameLevelResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameLevelsCollectionPageRequest(messages.Message):
    """ a levell collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)

GAME_LEVELS_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GameLevelsCollectionPageRequest
)
