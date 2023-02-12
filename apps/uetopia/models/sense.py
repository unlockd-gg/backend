import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class Sense(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    target_type = ndb.StringProperty()
    target_key = ndb.StringProperty()
    target_title = ndb.StringProperty(indexed=False)

    ref_type = ndb.StringProperty()
    ref_key = ndb.StringProperty()

    action = ndb.StringProperty(indexed=False)
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    amount = ndb.IntegerProperty(indexed=False)


class SenseResponse(messages.Message):
    """ a sense data """
    key = messages.StringField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    target_type = messages.StringField(4)
    target_key = messages.StringField(5)
    target_title = messages.StringField(6)
    ref_type = messages.StringField(7)
    ref_key = messages.StringField(8)
    action = messages.StringField(9)
    amount = messages.IntegerField(10)
