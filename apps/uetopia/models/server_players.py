import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class ServerPlayers(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    # Update each time an auth or de-auth occurs
    authTimestamp = ndb.DateTimeProperty()
    deAuthTimestamp = ndb.DateTimeProperty()
    authCount = ndb.IntegerProperty()
    deAuthCount = ndb.IntegerProperty()
    # Server stuff
    serverKeyId = ndb.IntegerProperty()
    serverTitle = ndb.StringProperty(indexed=False)
    # Server Shard ref
    serverShardKeyId = ndb.IntegerProperty(indexed=True)
    # Game stuff
    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    # currency stuff
    currencyStart = ndb.IntegerProperty(indexed=False)
    currencyCurrent = ndb.IntegerProperty(indexed=False)
    currencyEnd = ndb.IntegerProperty(indexed=False)
    currencyEarned = ndb.IntegerProperty(indexed=False)
    # user stuff
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)
    firebaseUser = ndb.StringProperty(indexed=False)
    # pending auth or deauth
    pending_authorize = ndb.BooleanProperty(indexed=False)
    pending_deauthorize = ndb.BooleanProperty(indexed=False)
    # status flags
    authorized = ndb.BooleanProperty(indexed=True)
    active = ndb.BooleanProperty(indexed=True)
    banned = ndb.BooleanProperty(indexed=False)
    online = ndb.BooleanProperty(indexed=False)
    # ladder details
    ladderRank = ndb.IntegerProperty(indexed=False)
    ## This was created for a matchmaker.  True value means it will not show in history.
    #internal_matchmaker = ndb.BooleanProperty(indexed=False)

    # admission related
    admission_paid = ndb.BooleanProperty(indexed=False)

    # experience
    experience = ndb.IntegerProperty(indexed=False)
    experience_total = ndb.IntegerProperty(indexed=False)

    #avatar_theme = ndb.StringProperty(indexed=False)

    ## Allow servers to store user information here.
    ## This is used for servers that want to store some persistant information about a user
    ## score, health, maybe a small inventory list.
    ## things that should persist even if a user rejoins a week later.
    ## allowing a string, so small json objects can be used

    ## TODO there will be more of this, as developers adopt
    user_state = ndb.StringProperty(indexed=False)


    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'firebaseUser':self.firebaseUser,
                u'authorized': self.authorized,
                u'active': self.active,
                u'banned': self.banned,
                u'userTitle': self.userTitle,
                u'ladderRank':self.ladderRank,
                u'currencyCurrent': self.currencyCurrent,
                u'online':self.online,
                u'userKeyId':self.userKeyId
        })

    def to_json_extended(self):
        return ({
                u'key_id': self.key.id(),
                u'authorized': self.authorized,
                u'active': self.active,
                u'banned': self.banned,
                u'userTitle': self.userTitle,
                u'userKeyId':self.userKeyId,
                u'ladderRank':self.ladderRank,
                u'online':self.online,
                u'authCount': self.authCount,
                u'serverKeyId': self.serverKeyId,
                u'serverTitle': self.serverTitle,
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                u'firebaseUser':self.firebaseUser,
                u'currencyCurrent': self.currencyCurrent,
                u'currencyEarned': self.currencyEarned,
                u'authorizing': self.pending_authorize,
                u'deauthorizing': self.pending_deauthorize,
                u'authorized': self.authorized,
                u'active': self.active,
                u'banned': self.banned,
                u'online': self.online,
                u'ladderRank': self.ladderRank,
                u'admission_paid': self.admission_paid,
                u'experience': self.experience_total,
                u'user_state': self.user_state,
        })


### PROTORPC MODELS FOR ENDPOINTS

class ServerPlayerBasicResponse(messages.Message):
    """ a server user member's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    userKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    serverKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    authorized = messages.BooleanField(4)
    active = messages.BooleanField(5)
    banned = messages.BooleanField(6)
    title = messages.StringField(7)
    ladderRank = messages.IntegerField(8)
    admission_paid = messages.BooleanField(9)
    currencyCurrent = messages.IntegerField(10, variant=messages.Variant.INT32)
    online = messages.BooleanField(12)

class ServerPlayerResponse(messages.Message):
    """ a server user member's data """
    created = message_types.DateTimeField(1)
    serverKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    serverName =messages.StringField(3)
    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameName = messages.StringField(5)
    currencyStart = messages.IntegerField(6)
    currencyCurrent = messages.IntegerField(7)
    currencyEnd = messages.IntegerField(8)
    currencyEarned = messages.IntegerField(9)
    userKeyId = messages.IntegerField(10, variant=messages.Variant.INT32)
    name = messages.StringField(11)
    pending_authorize = messages.BooleanField(12)
    pending_deauthorize = messages.BooleanField(13)
    authorized = messages.BooleanField(14)
    active = messages.BooleanField(15)
    banned = messages.BooleanField(16)
    ladderRank = messages.IntegerField(17)
    key_id = messages.IntegerField(18, variant=messages.Variant.INT32)
    experience = messages.IntegerField(19, variant=messages.Variant.INT32)
    experience_total = messages.IntegerField(20, variant=messages.Variant.INT32)
    online = messages.BooleanField(21)
    admission_paid = messages.BooleanField(22)
    serverClusterKeyId = messages.IntegerField(30, variant=messages.Variant.INT32)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

SERVER_PLAYER_RESOURCE = endpoints.ResourceContainer(
    ServerPlayerResponse
)

class ServerUserMemberCollection(messages.Message):
    """ multiple transactions """
    serverplayers = messages.MessageField(ServerPlayerResponse, 1, repeated=True)
    message = messages.StringField(2)

class ServerPlayerServerKeyRequest(messages.Message):
    """ a server's data """
    key_id = messages.IntegerField(1)

SERVER_PLAYER_SERVER_KEY_RESOURCE = endpoints.ResourceContainer(
    ServerPlayerServerKeyRequest
)
