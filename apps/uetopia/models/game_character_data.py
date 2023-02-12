import endpoints
import datetime
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GameCharacterData(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)

    groupKeyId = ndb.IntegerProperty(indexed=False)
    groupTag = ndb.StringProperty(indexed=False)

    # Firebase auth
    firebaseUser = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)

    locked = ndb.BooleanProperty(indexed=False)
    lock_timestamp = ndb.DateTimeProperty(indexed=False)
    locked_by_serverKeyId = ndb.IntegerProperty(indexed=True)

    online = ndb.BooleanProperty()

    rank = ndb.IntegerProperty(indexed=True)
    score = ndb.IntegerProperty(indexed=False)
    experience = ndb.IntegerProperty(indexed=False)
    experienceThisLevel = ndb.IntegerProperty(indexed=False)
    level = ndb.IntegerProperty(indexed=False)

    ## Arbitrary text that servers can use to retrieve and store common information about a user
    inventory = ndb.TextProperty(indexed=False)
    equipment = ndb.TextProperty(indexed=False)
    abilities = ndb.TextProperty(indexed=False)
    interface = ndb.TextProperty(indexed=False)
    crafting = ndb.TextProperty(indexed=False)
    recipes = ndb.TextProperty(indexed=False)
    character = ndb.TextProperty(indexed=False)

    ## Location information
    ## Used by servers to know where the user came from
    coordLocationX = ndb.FloatProperty(indexed=False)
    coordLocationY = ndb.FloatProperty(indexed=False)
    coordLocationZ = ndb.FloatProperty(indexed=False)

    zoneName = ndb.StringProperty(indexed=False)
    zoneKey = ndb.StringProperty(indexed=False)  ## this is not an internal appengine key, but servers can set/read it themselves.

    ## game auto auth settings - only needed in gamePlayer
    #autoAuth = ndb.BooleanProperty(indexed=False)
    #autoAuthThreshold = ndb.IntegerProperty(indexed=False)
    #autoTransfer = ndb.BooleanProperty(indexed=False)

    ## keep track of last server and serverplayer keys
    lastServerClusterKeyId = ndb.IntegerProperty(indexed=True)
    lastServerKeyId = ndb.IntegerProperty(indexed=False)
    lastServerPlayerKeyId = ndb.IntegerProperty(indexed=False)
    lastServerLinkKeyId = ndb.IntegerProperty(indexed=False)
    #lastServerLinkPairKeyId = ndb.IntegerProperty(indexed=False)
    ## keep track of homeserver keys TODO
    homeServerClusterKeyId = ndb.IntegerProperty(indexed=False)
    homeServerKeyId = ndb.IntegerProperty(indexed=False)
    homeServerPlayerKeyId = ndb.IntegerProperty(indexed=False)
