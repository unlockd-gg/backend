import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types



class MatchTaskStatus(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)

    region = ndb.StringProperty(indexed=True)
    mode = ndb.StringProperty(indexed=True) ## this is the onlineSubsystemReference

    matchmakerAlgorithm = ndb.StringProperty(indexed=True)

    ## these are labelled as "rank" but they are used for all MM types as min/mid/max
    rankMin = ndb.IntegerProperty(indexed=True)
    rankMedian = ndb.IntegerProperty(indexed=False)
    rankMax = ndb.IntegerProperty(indexed=False)

    successful_runs = ndb.IntegerProperty(indexed=False)
    successful_match_count = ndb.IntegerProperty(indexed=False)
    failed_runs = ndb.IntegerProperty(indexed=False)
    consecutive_failed_runs = ndb.IntegerProperty(indexed=False)

    playersPerTeam = ndb.IntegerProperty(indexed=False)
    teams = ndb.IntegerProperty(indexed=False)

    discord_subscribe = ndb.BooleanProperty(indexed=False) # non-admin
    discord_webhook = ndb.StringProperty(indexed=False)  ## admin related feed
