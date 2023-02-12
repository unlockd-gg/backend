import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class MatchResultsUser(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    serverKeyId = ndb.IntegerProperty()
    serverTitle = ndb.StringProperty(indexed=False)

    matchResultsKeyId = ndb.IntegerProperty()

    userKeyId = ndb.IntegerProperty() ## to fill in later via batch process
    userName = ndb.StringProperty(indexed=False)

    experience = ndb.IntegerProperty(indexed=False)
    score = ndb.IntegerProperty(indexed=False)
    rank = ndb.IntegerProperty(indexed=False)
    playstyle_killer = ndb.IntegerProperty(indexed=False)
    playstyle_achiever = ndb.IntegerProperty(indexed=False)
    playstyle_explorer = ndb.IntegerProperty(indexed=False)
    playstyle_socializer = ndb.IntegerProperty(indexed=False)

    weapon = ndb.StringProperty(indexed=False)

    postiveCount = ndb.IntegerProperty(indexed=False)
    negativeCount = ndb.IntegerProperty(indexed=False)


    killedUserKeyIds = ndb.IntegerProperty(repeated=True, indexed=False)  ## to fill in later via batch process
    killedUserTitles = ndb.StringProperty(repeated=True, indexed=False)
    events = ndb.StringProperty(repeated=True, indexed=False)

class MatchResultsUserResponse(messages.Message):
    """ a MatchResultsUser's data """
    key = messages.StringField(1)
    postiveCount = messages.IntegerField(2, variant=messages.Variant.INT32)
    negativeCount = messages.IntegerField(3, variant=messages.Variant.INT32)
    weapon = messages.StringField(4)
