import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Drops(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    expirationDate = ndb.DateTimeProperty(indexed=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)

    ## we might want to connect this up to a badge?  It could be used to give drops to players that need the badge to redeem it.
    ## think about this.

    userKeyId = ndb.IntegerProperty(indexed=True)
    userTitle = ndb.StringProperty(indexed=False)

    gamePlayerKeyId = ndb.IntegerProperty(indexed=True)
    #gamePlayerTitle = ndb.StringProperty(indexed=False)

    uiIcon = ndb.StringProperty(indexed=False)
    data = ndb.TextProperty(indexed=False)
    tier = ndb.IntegerProperty(indexed=False)

    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'uiIcon': self.uiIcon,
                u'expires': self.expirationDate.isoformat(),
                u'tier': self.tier
        })
