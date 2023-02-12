import endpoints
import datetime
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class ServerClusterPlayers(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)
    serverClusterKeyId = ndb.IntegerProperty(indexed=True)
    serverClusterTitle = ndb.StringProperty(indexed=False)


    # Firebase auth
    firebaseUser = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)

    locked = ndb.BooleanProperty(indexed=False)
    lock_timestamp = ndb.DateTimeProperty(indexed=False)
    locked_by_serverKeyId = ndb.IntegerProperty(indexed=False)

    online = ndb.BooleanProperty()

    rank = ndb.IntegerProperty(indexed=False)
    score = ndb.IntegerProperty(indexed=False)
    experience = ndb.IntegerProperty(indexed=False)

    ## Arbitrary text that servers can use to retrieve and store common information about a user
    inventory = ndb.TextProperty(indexed=False)
    equipment = ndb.TextProperty(indexed=False)
    abilities = ndb.TextProperty(indexed=False)
    interface = ndb.TextProperty(indexed=False)

    ## Location information
    ## Used by servers to know where the user came from
    coordLocationX = ndb.FloatProperty(indexed=False)
    coordLocationY = ndb.FloatProperty(indexed=False)
    coordLocationZ = ndb.FloatProperty(indexed=False)

    zoneName = ndb.StringProperty(indexed=False)
    zoneKey = ndb.StringProperty(indexed=False)  ## this is not an internal appengine key, but servers can set/read it themselves.

    ## game auto auth settings
    #autoAuth = ndb.BooleanProperty(indexed=False)
    #autoAuthThreshold = ndb.IntegerProperty(indexed=False)
    autoTransfer = ndb.BooleanProperty(indexed=False)

    ## keep track of last server and serverplayer keys

    lastServerKeyId = ndb.IntegerProperty(indexed=False)
    lastServerPlayerKeyId = ndb.IntegerProperty(indexed=False)
    ## keep track of homeserver keys TODO

    homeServerKeyId = ndb.IntegerProperty(indexed=False)
    homeServerPlayerKeyId = ndb.IntegerProperty(indexed=False)




    def to_json(self):
        now = datetime.datetime.now()
        return ({
                u'key_id': str(self.key.id()),
                #u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                #u'userAvatarTheme': self.userAvatarTheme,
                u'rank': self.rank,
                u'score': self.score,
                u'zoneName': self.zoneName,
                u'firebaseUser': self.firebaseUser,
                u'picture': self.picture,
                u'updated': now.isoformat(' ')
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
                u'zoneName': self.zoneName,
                #u'firebaseUser': self.firebaseUser,
                u'picture': self.picture,
                u'online': self.online,
                u'updated': now.isoformat(' ')
        })


class ServerClusterPlayerResponse(messages.Message):
    """ a ServerCluster player's data """
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
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class ServerClusterPlayerRequest(messages.Message):
    """ a ServerCluster player's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    approved = messages.BooleanField(2)
    roleKey = messages.StringField(3)
    #autoAuth = messages.BooleanField(4)
    #autoAuthThreshold = messages.IntegerField(5, variant=messages.Variant.INT32)
    autoTransfer = messages.BooleanField(6)

SERVER_CLUSTER_PLAYER_RESOURCE = endpoints.ResourceContainer(
    ServerClusterPlayerRequest
)
