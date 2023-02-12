import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GroupGameUsers(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty()

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty()

    groupUserKeyId = ndb.IntegerProperty()

    vettingEnabled = ndb.BooleanProperty()
    vettingCompleted = ndb.BooleanProperty()
    vettingFinalized = ndb.BooleanProperty()

    gkpAmount = ndb.FloatProperty()
    gkpVettingRemaining = ndb.IntegerProperty()
