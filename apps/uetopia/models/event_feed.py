from google.appengine.ext import ndb


class EventFeed(ndb.Model):
    """ Tracks sitewide events
        This provides the data for the feed on the homepage, gamepage, group and user pages

    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    gameDisplayText = ndb.StringProperty(indexed=False)

    serverKeyId = ndb.IntegerProperty()
    serverTitle = ndb.StringProperty(indexed=False)
    serverDisplayText = ndb.StringProperty(indexed=False)

    serverClusterKeyId = ndb.IntegerProperty()
    serverClusterTitle = ndb.StringProperty(indexed=False)

    matchKeyId = ndb.IntegerProperty()
    matchTitle = ndb.StringProperty(indexed=False)
    matchDisplayText = ndb.StringProperty(indexed=False)

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)
    groupDisplayText = ndb.StringProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)
    userDisplayText = ndb.StringProperty(indexed=False)

    eventType = ndb.StringProperty()

    text = ndb.StringProperty(indexed=False)
    icon = ndb.StringProperty(indexed=False)

    value = ndb.IntegerProperty(indexed=False)

    def to_json_for_game(self):
        return ({
                u'key_id': self.key.id(),
                u'icon': self.icon,
                u'text': self.gameDisplayText,
                u'event_type': self.eventType,
                u'created': self.created.isoformat()

        })

    def to_json_for_group(self):
        return ({
                u'key_id': self.key.id(),
                u'icon': self.icon,
                u'text': self.groupDisplayText,
                u'event_type': self.eventType,
                u'created': self.created.isoformat()

        })

    def to_json_for_user(self):
        return ({
                u'key_id': self.key.id(),
                u'icon': self.icon,
                u'text': self.userDisplayText,
                u'event_type': self.eventType,
                u'created': self.created.isoformat()

        })
