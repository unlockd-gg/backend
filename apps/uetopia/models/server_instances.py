import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class ServerInstances(ndb.Model):
    """ Server Instances are used to calculate server costs over time.  These are NOT the same as server instanced mode - which is part of the server model """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    serverKeyId = ndb.IntegerProperty(indexed=True)
    serverTitle = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)

    machine_type = ndb.StringProperty(indexed=False)
    region_name = ndb.StringProperty(indexed=False)

    continuous_server_creating_timestamp = ndb.DateTimeProperty(indexed=False)
    continuous_server_destroying_timestamp = ndb.DateTimeProperty(indexed=False)

    uptime_minutes_billable = ndb.IntegerProperty(indexed=False)

    serverClusterKeyId = ndb.IntegerProperty()
    serverClusterTitle = ndb.StringProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()
    #gameKeyId = ndb.IntegerProperty()

    processed = ndb.BooleanProperty(indexed=True)
    instanceType = ndb.StringProperty(indexed=True) # server, match
