import json
from google.appengine.ext import ndb


class MatchResults(ndb.Model):
    ## despite the name this is not for matchmaker
    ## this is for server "SubmitMatchData"
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    matchKeyId = ndb.IntegerProperty()
    matchTitle = ndb.StringProperty(indexed=False)
    mapTitle = ndb.StringProperty(indexed=False)
    serverKeyId = ndb.IntegerProperty()
    serverTitle = ndb.StringProperty(indexed=False)

    ## player data is stored in the match player record

    def to_dict(self):
        return ({
                u'key_id': str(self.key.id()),
                u'created': str(self.created),
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                u'matchKeyId': self.serverKey,
                u'matchTitle': self.serverTitle,

        })
