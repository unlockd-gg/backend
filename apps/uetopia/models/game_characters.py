import endpoints
import datetime
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from apps.uetopia.models.game_character_data import GameCharacterData

class GameCharacters(GameCharacterData):
    ## Inherets from GameCharacterData
    currentlySelectedActive = ndb.BooleanProperty(indexed=False)
    characterType = ndb.StringProperty(indexed=False) # regular, hardcore
    characterAlive = ndb.BooleanProperty(indexed=False)
    characterState = ndb.StringProperty(indexed=False)

    characterCustom = ndb.TextProperty(indexed=False)

    title = ndb.StringProperty()
    description = ndb.TextProperty(indexed=False)


    def to_json(self):
        now = datetime.datetime.now()
        return ({
                u'key_id': str(self.key.id()),
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                #u'userAvatarTheme': self.userAvatarTheme,
                u'rank': self.rank,
                u'score': self.score,
                u'zoneName': self.zoneName,
                u'firebaseUser': self.firebaseUser,
                u'picture': self.picture,
                u'updated': now.isoformat(' '),
                u'groupKeyId':self.groupKeyId,
                u'groupTag':self.groupTag
        })
    def to_json_public(self):
        now = datetime.datetime.now()
        return ({
                u'key_id': str(self.key.id()),
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                #u'userAvatarTheme': self.userAvatarTheme,
                u'rank': self.rank,
                u'score': self.score,
                u'level': self.level,
                u'zoneName': self.zoneName,
                #u'firebaseUser': self.firebaseUser,
                u'picture': self.picture,
                u'online': self.online,
                u'updated': now.isoformat(' '),
                u'groupKeyId':self.groupKeyId,
                u'groupTag':self.groupTag,
                u'title': self.title
        })

class GameCharacterGetRequest(messages.Message):
    """ a gc's key """
    key_id = messages.StringField(1)
    developerRequest = messages.BooleanField(20)
    gameCharacterKeyId = messages.IntegerField(25, variant=messages.Variant.INT32)

GAME_CHARACTER_GET_RESOURCE = endpoints.ResourceContainer(
    GameCharacterGetRequest
)

class GameCharacterCreateRequest(messages.Message):
    """ a Game Character """
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    gameKeyIdStr = messages.StringField(15)  ## Unreal wants string!
    characterType = messages.StringField(5)
    characterState = messages.StringField(6)
    characterCustom = messages.StringField(7)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)


GAME_CHARACTER_CREATE_RESOURCE = endpoints.ResourceContainer(
    GameCharacterCreateRequest
)

class GameCharacterResponse(messages.Message):
    """ a Game Character  """
    key_id = messages.StringField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)

    characterType = messages.StringField(5)
    characterState = messages.StringField(6)
    characterAlive = messages.BooleanField(7)
    currentlySelectedActive = messages.BooleanField(8)
    characterCustom = messages.StringField(9)

    userKeyId = messages.IntegerField(202)
    userTitle = messages.StringField(203)
    userAvatarTheme = messages.StringField(204)
    rank = messages.IntegerField(205, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(206, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(207)
    online = messages.BooleanField(208)
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

    response_message = messages.StringField(940)
    response_successful = messages.BooleanField(950)



class GameCharacterUpdateRequest(messages.Message):
    """ a Game Character  """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)

    characterType = messages.StringField(5)
    characterState = messages.StringField(6)
    characterAlive = messages.BooleanField(7)
    currentlySelectedActive = messages.BooleanField(8)
    characterCustom = messages.StringField(9)

    userKeyId = messages.IntegerField(202)
    userTitle = messages.StringField(203)
    userAvatarTheme = messages.StringField(204)
    rank = messages.IntegerField(205, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(206, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(207)
    online = messages.BooleanField(208)
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

    response_message = messages.StringField(940)
    response_successful = messages.BooleanField(950)

GAME_CHARACTER_UPDATE_RESOURCE = endpoints.ResourceContainer(
    GameCharacterUpdateRequest
)

class GameCharacterCollectionPageRequest(messages.Message):
    """ a VendorType's data """
    cursor = messages.StringField(1)
    gameKeyId = messages.IntegerField(4)
    gameKeyIdStr = messages.StringField(5)  ## Unreal wants string!
    developerRequest = messages.BooleanField(15)  ## devs can request for thier game
    userKeyId = messages.IntegerField(20)  # with a userKey

GAME_CHARACTER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GameCharacterCollectionPageRequest
)

class GameCharacterCollection(messages.Message):
    """ multiple GameCharacters """
    characters = messages.MessageField(GameCharacterResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    mm_region = messages.StringField(4) # convenience pass this 
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
