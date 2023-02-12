import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GroupRaids(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty()

    teamKeyId = ndb.IntegerProperty()
    teamTitle = ndb.StringProperty()

    captainKeyId = ndb.IntegerProperty()
    captainTitle = ndb.StringProperty()

    title = ndb.StringProperty()
    description = ndb.StringProperty()

    started = ndb.BooleanProperty()
    complete = ndb.BooleanProperty()
    finalized = ndb.BooleanProperty()
    ## TODO add more group permissions

    #startedTime = ndb.DateTimeProperty()
    completedTime = ndb.DateTimeProperty()
    finalizedTime = ndb.DateTimeProperty()

    vettingEnabled = ndb.BooleanProperty()
    vettingCompleted = ndb.BooleanProperty()
