import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class MatchTeams(ndb.Model):
    """ A match team is one or more "teams" that have been matchmade and will fight together in a match.
        This is used primarily for tracking hostorical win/loss information
        But, it also provides the unique keyId for the match team chat channel

    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)

    matchKeyId = ndb.IntegerProperty(indexed=True)
    matchTitle = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)

    teamIndex = ndb.IntegerProperty(indexed=False)

    win = ndb.BooleanProperty(indexed=False)
