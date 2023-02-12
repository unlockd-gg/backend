import endpoints
import datetime
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from apps.uetopia.models.game_character_data import GameCharacterData

class GamePlayers(GameCharacterData):
    ## Inherets from GameCharacterData

    ## game auto auth settings
    #autoAuth = ndb.BooleanProperty(indexed=False)
    #autoAuthThreshold = ndb.IntegerProperty(indexed=False)
    autoTransfer = ndb.BooleanProperty(indexed=False)

    showGameOnProfile = ndb.BooleanProperty(indexed=False)

    characterCurrentKeyId = ndb.IntegerProperty(indexed=False)
    characterCurrentTitle = ndb.StringProperty(indexed=False)
    characterMaxAllowedCount = ndb.IntegerProperty(indexed=False)

    ## metagame stuff
    apiKey = ndb.StringProperty(indexed=True) ## this is used for metagame connect ONLY.  It is erased after validation
    metagame_connected = ndb.BooleanProperty(indexed=False)

    ## Badges
    badgeTags = ndb.StringProperty(repeated=True, indexed=False)

    banned = ndb.BooleanProperty(indexed=False)


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
                u'groupTag':self.groupTag
        })


class GamePlayerResponse(messages.Message):
    """ a game player's data """
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

    apiKey = messages.StringField(201) ## temporary security code for metagame

    characterMaxAllowedCount = messages.IntegerField(301, variant=messages.Variant.INT32)

    response_message = messages.StringField(940)
    response_successful = messages.BooleanField(950)

class GamePlayerRequest(messages.Message):
    """ a game player's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    approved = messages.BooleanField(2)
    roleKey = messages.StringField(3)
    #autoAuth = messages.BooleanField(4)
    #autoAuthThreshold = messages.IntegerField(5, variant=messages.Variant.INT32)
    autoTransfer = messages.BooleanField(6)
    lastServerClusterKeyId = messages.IntegerField(7, variant=messages.Variant.INT32)
    serverKeyId = messages.IntegerField(8, variant=messages.Variant.INT32) ## for specifying a server directly
    serverKeyIdStr = messages.StringField(9) ## UE clinets will be sending a string
    showGameOnProfile = messages.BooleanField(15)
    developer = messages.BooleanField(20)  ## devs can request for thier game
    #gamePlayerKeyId = messages.IntegerField(25)  # with a key_id
    gamePlayerKeyId = messages.IntegerField(25, variant=messages.Variant.INT32)

    score = messages.IntegerField(51, variant=messages.Variant.INT32)
    experience = messages.IntegerField(52, variant=messages.Variant.INT32)
    experienceThisLevel = messages.IntegerField(53, variant=messages.Variant.INT32)
    level = messages.IntegerField(54, variant=messages.Variant.INT32)
    inventory = messages.StringField(55)
    equipment = messages.StringField(56)
    abilities = messages.StringField(57)
    interface = messages.StringField(58)
    crafting = messages.StringField(59)
    recipes = messages.StringField(60)
    character = messages.StringField(61)
    coordLocationX = messages.FloatField(62)
    coordLocationY = messages.FloatField(63)
    coordLocationZ = messages.FloatField(64)
    zoneName = messages.StringField(65)
    zoneKey = messages.StringField(66)
    lastServerKeyId = messages.IntegerField(67, variant=messages.Variant.INT32)
    rank = messages.IntegerField(68, variant=messages.Variant.INT32)
    characterMaxAllowedCount = messages.IntegerField(301, variant=messages.Variant.INT32)

GAME_PLAYER_RESOURCE = endpoints.ResourceContainer(
    GamePlayerRequest
)

class GamePlayersCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    groupGameKeyId = messages.IntegerField(5)
    gamePlayerKeyId = messages.IntegerField(6)

GAME_PLAYER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GamePlayersCollectionPageRequest
)

class GamePlayersCollection(messages.Message):
    """ multiple players """
    game_players = messages.MessageField(GamePlayerResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)
