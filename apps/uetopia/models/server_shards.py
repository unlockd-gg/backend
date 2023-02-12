import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class ServerShards(ndb.Model):
    """ Server Shards connect individual shards to the parent shard template.   These store unimportant data only, and may violate the one second rule."""
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    serverShardTemplateKeyId = ndb.IntegerProperty(indexed=True)
    serverShardTemplateTitle = ndb.StringProperty(indexed=False)

    serverShardKeyId = ndb.IntegerProperty(indexed=True)
    serverShardTitle = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)

    serverClusterKeyId = ndb.IntegerProperty(indexed=False)
    serverClusterTitle = ndb.StringProperty(indexed=False)

    playerCount = ndb.IntegerProperty(indexed=True)
    playerCapacityThreshold = ndb.IntegerProperty(indexed=False)
    playerCapacityMaximum = ndb.IntegerProperty(indexed=False)

    online = ndb.BooleanProperty(indexed=True)

    shardId = ndb.IntegerProperty(indexed=True)
    hostConnectionLink = ndb.StringProperty(indexed=False)

    def to_json(self):
        return ({
            #u'targetServerTitle': self.targetServerTitle,
            u'targetServerKeyId': str(self.serverShardKeyId),
            u'online': self.online,
            u'hostConnectionLink':self.hostConnectionLink or "",
            u'shardId':self.shardId,
            u'playerCount':self.playerCount,
            u'playerCapacityMaximum':self.playerCapacityMaximum
        })
