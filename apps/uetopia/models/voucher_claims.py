import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class VoucherClaims(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)
    voucherKeyId = ndb.IntegerProperty()
    voucherTitle = ndb.StringProperty(indexed=False)

    autoRefresh = ndb.BooleanProperty(indexed=False)
