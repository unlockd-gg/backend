import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class ServerShardPlaceholder(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)
    serverClusterKeyId = ndb.IntegerProperty(indexed=True)
    serverShardTemplateKeyId = ndb.IntegerProperty(indexed=True) ## parent
    serverShardTemplateTitle = ndb.StringProperty(indexed=False)

    serverShardKeyId = ndb.IntegerProperty(indexed=True) ## shard  
    serverShardTitle = ndb.StringProperty(indexed=False)
    serverAssigned = ndb.BooleanProperty(indexed=True)

    serverKeyId = ndb.IntegerProperty(indexed=True) ## server

    userKeyId = ndb.IntegerProperty(indexed=True) ## user
    userTitle = ndb.StringProperty(indexed=False)
    firebaseUser = ndb.StringProperty(indexed=False)

    vm_region = ndb.StringProperty(indexed=True)
    vm_zone = ndb.StringProperty(indexed=False)

    inParty = ndb.BooleanProperty(indexed=False)
    partySize = ndb.IntegerProperty(indexed=False)
