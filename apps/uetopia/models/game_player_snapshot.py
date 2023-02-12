import endpoints
import datetime
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from apps.uetopia.models.game_character_data import GameCharacterData

class GamePlayerSnapshot(GameCharacterData):
    ## Inherets from GameCharacterData
    title = ndb.StringProperty()

    characterRecord = ndb.BooleanProperty(indexed=False) ## conflicts with character (TEXT) in game_character_data model
    characterKeyId = ndb.IntegerProperty(indexed=True)

    player = ndb.BooleanProperty(indexed=False)
    gamePlayerKeyId = ndb.IntegerProperty(indexed=True)


class GamePlayerSnapshotResponse(messages.Message):
    """ a game player snapshot's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    userKeyId = messages.IntegerField(2)
    userTitle = messages.StringField(3)
    userAvatarTheme = messages.StringField(4)
    rank = messages.IntegerField(5, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(7)
    online = messages.BooleanField(8)
    #message = messages.StringField(9)
    #autoAuth = messages.BooleanField(10)
    #autoAuthThreshold = messages.IntegerField(11, variant=messages.Variant.INT32)
    autoTransfer = messages.BooleanField(12)
    gameTrustable = messages.BooleanField(13)
    lastServerClusterKeyId = messages.IntegerField(14, variant=messages.Variant.INT32)
    showGameOnProfile = messages.BooleanField(15)

    created = messages.StringField(21) #DATETIME
    modified = messages.StringField(22) #DATETIME

    ## additional values for developer
    locked = messages.BooleanField(101)
    locked_by_serverKeyId = messages.IntegerField(102, variant=messages.Variant.INT32)
    #rank = messages.IntegerField(103, variant=messages.Variant.INT32)
    score = messages.IntegerField(104, variant=messages.Variant.INT32)
    experience = messages.IntegerField(105, variant=messages.Variant.INT32)
    experienceThisLevel = messages.IntegerField(106, variant=messages.Variant.INT32)
    level = messages.IntegerField(107, variant=messages.Variant.INT32)
    inventory = messages.StringField(108)
    equipment = messages.StringField(109)
    abilities = messages.StringField(121)
    interface = messages.StringField(122)
    crafting = messages.StringField(123)
    recipes = messages.StringField(124)
    character = messages.StringField(125)
    coordLocationX = messages.FloatField(126)
    coordLocationY = messages.FloatField(127)
    coordLocationZ = messages.FloatField(128)
    zoneName = messages.StringField(129)
    zoneKey = messages.StringField(141)
    #lastServerClusterKeyId = messages.IntegerField(142, variant=messages.Variant.INT32)
    lastServerKeyId = messages.IntegerField(143, variant=messages.Variant.INT32)

    characterRecord = messages.BooleanField(150)
    characterKeyId = messages.IntegerField(151, variant=messages.Variant.INT32)

    player = messages.BooleanField(152)
    gamePlayerKeyId = messages.IntegerField(153, variant=messages.Variant.INT32)

    created = messages.StringField(200) #DATETIME
    title = messages.StringField(201)

    response_message = messages.StringField(940)
    response_successful = messages.BooleanField(950)

class GamePlayerSnapshotRequest(messages.Message):
    """ a game player's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32) ## key is forbidden incoming
    developerRequest = messages.BooleanField(3)


GAME_PLAYER_SNAPSHOT_RESOURCE = endpoints.ResourceContainer(
    GamePlayerSnapshotRequest
)

class GamePlayerSnapshotCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gamePlayerKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    characterKeyId = messages.IntegerField(7, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(8, variant=messages.Variant.INT32)

GAME_PLAYER_SNAPSHOT_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GamePlayerSnapshotCollectionPageRequest
)

class GamePlayerSnapshotCollection(messages.Message):
    """ multiple player snapshots """
    snapshots = messages.MessageField(GamePlayerSnapshotResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)
