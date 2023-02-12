import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class Orders(ndb.Model):
    """ Orders are created when a player initiates a CRED purchase """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    userKeyId = ndb.IntegerProperty(indexed=True)
    userTitle = ndb.StringProperty(indexed=False)
    firebaseUser = ndb.StringProperty(indexed=False)

    processor = ndb.StringProperty()
    value_in_cred = ndb.IntegerProperty()
    value_in_usd = ndb.FloatProperty()

    status_paid = ndb.BooleanProperty(indexed=False)
    status_confirmed = ndb.BooleanProperty(indexed=False)
