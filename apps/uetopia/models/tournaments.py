import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

from apps.uetopia.models.teams import TeamResponse
from apps.uetopia.models.match import MatchCollection
from apps.uetopia.models.tournament_sponsors import TournamentSponsorResponse

class Tournaments(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    #platformKeyId = ndb.IntegerProperty()
    #platformTitle = ndb.StringProperty()

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    groupMembersOnly = ndb.BooleanProperty()
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)

    hostUserKeyId = ndb.IntegerProperty()
    hostUserTitle = ndb.StringProperty(indexed=False)

    signupStartTime = ndb.DateTimeProperty(indexed=False)
    signupEndTime = ndb.DateTimeProperty(indexed=False)

    playStartTime = ndb.DateTimeProperty(indexed=False)
    playEndTime = ndb.DateTimeProperty(indexed=False)

    ## Using game mode instead of the team size ints.
    gameModeKeyId = ndb.IntegerProperty(indexed=False)
    gameModeTitle = ndb.StringProperty(indexed=False)
    teamMin = ndb.IntegerProperty(indexed=False)  # the minimum number of teams to start the tournament
    teamMax = ndb.IntegerProperty(indexed=False)  # the maximum number of teams that can join the tournament

    region = ndb.StringProperty(indexed=False)

    playerBuyIn = ndb.IntegerProperty(indexed=False)
    additionalPrizeFromHost = ndb.IntegerProperty(indexed=False)
    prizeDistributionType = ndb.StringProperty(indexed=False) # winner takes all, 70-20-10 split, etc
    currencyBalance = ndb.IntegerProperty(indexed=False) ## total CRED on hand
    estimatedTotalWinnings = ndb.IntegerProperty(indexed=False) ## total cred awardable (minus server fees)
    server_fees = ndb.IntegerProperty(indexed=False)

    total_players = ndb.IntegerProperty(indexed=False)
    total_buyin_amount = ndb.IntegerProperty(indexed=False)

    ## round tracking
    total_rounds = ndb.IntegerProperty(indexed=False)
    current_round = ndb.IntegerProperty(indexed=False)

    ## State flags
    initialized = ndb.BooleanProperty()
    signupsStarted = ndb.BooleanProperty()
    signupsFinished = ndb.BooleanProperty()
    playStarted = ndb.BooleanProperty()
    playFinished = ndb.BooleanProperty()
    completed = ndb.BooleanProperty()
    finalized = ndb.BooleanProperty()
    unplayedExpired = ndb.BooleanProperty()

    resultDisplayText = ndb.StringProperty(indexed=False)
    ## TODO some kind of wrapup data.  winners, winnings etc

    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                u'playerBuyIn': self.playerBuyIn,
                u'gameModeTitle':self.gameModeTitle,
                u'signupsFinished':self.signupsFinished,
                u'additionalPrizeFromHost':self.additionalPrizeFromHost,
                u'signupsStarted':self.signupsStarted,
                u'playStarted':self.playStarted,
                u'playFinished':self.playFinished,
                u'region':self.region,
                u'prizeDistributionType':self.prizeDistributionType,
                u'estimatedTotalWinnings':self.estimatedTotalWinnings
        })

    def to_json_with_teams_and_tiers(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'gameTitle': self.gameTitle,
                u'playerBuyIn': self.playerBuyIn,
                u'gameModeTitle':self.gameModeTitle,
                u'signupsFinished':self.signupsFinished,
                u'additionalPrizeFromHost':self.additionalPrizeFromHost,
                u'signupsStarted':self.signupsStarted,
                u'playStarted':self.playStarted,
                u'playFinished':self.playFinished,
                u'region':self.region,
                u'prizeDistributionType':self.prizeDistributionType,
                u'estimatedTotalWinnings':self.estimatedTotalWinnings,
                u'teams':self.teams,
                u'tiers':self.tiers
        })

    def to_json_with_teams_tiers_and_sponsors(self):
        return ({
                u'key_id': self.key.id(),
                u'hostUserKeyId': self.hostUserKeyId,
                u'title': self.title,
                u'gameTitle': self.gameTitle,
                u'playerBuyIn': self.playerBuyIn,
                u'gameModeTitle':self.gameModeTitle,
                u'signupsFinished':self.signupsFinished,
                u'additionalPrizeFromHost':self.additionalPrizeFromHost,
                u'signupsStarted':self.signupsStarted,
                u'playStarted':self.playStarted,
                u'playFinished':self.playFinished,
                u'region':self.region,
                u'prizeDistributionType':self.prizeDistributionType,
                u'estimatedTotalWinnings':self.estimatedTotalWinnings,
                u'teams':self.teams,
                u'tiers':self.tiers,
                u'sponsors':self.sponsors
        })



### PROTORPC MODELS FOR ENDPOINTS

class TournamentGetRequest(messages.Message):
    """ a Tournament's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    keyIdStr = messages.StringField(2) ## STR if it's coming from UE clients
    gameKeyIdStr = messages.StringField(5) ## STR if it's coming from UE clients


TOURNAMENT_GET_RESOURCE = endpoints.ResourceContainer(
    TournamentGetRequest
)

class TournamentCreateRequest(messages.Message):
    """ a Tournament's data """
    gameKeyId = messages.IntegerField(1, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    gameModeKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    gameMode = messages.StringField(4) ## we don't have the key if it's coming from UE clients
    gameKeyIdStr = messages.StringField(5) ## STR if it's coming from UE clients

    title = messages.StringField(13)
    description = messages.StringField(14)

    #teamSize = messages.IntegerField(15)
    teamMin = messages.IntegerField(16)
    teamMax = messages.IntegerField(17)

    playerBuyIn = messages.IntegerField(18)
    additionalPrizeFromHost = messages.IntegerField(19)

    region = messages.StringField(21)

    groupMembersOnly = messages.BooleanField(110)
    prizeDistributionType = messages.StringField(111)

TOURNAMENT_CREATE_RESOURCE = endpoints.ResourceContainer(
    TournamentCreateRequest
)

class TournamentResponse(messages.Message):
    """ a Tournament's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    keyIdStr = messages.StringField(2) ## STR if it's coming from UE clients
    title = messages.StringField(12)
    description = messages.StringField(13)

    gameModeKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    groupTitle = messages.StringField(6)
    gameModeTitle = messages.StringField(7)

    #teamSize = messages.IntegerField(16)
    teamMin = messages.IntegerField(17)
    teamMax = messages.IntegerField(18)

    playerBuyIn = messages.IntegerField(19)

    region = messages.StringField(21)

    additionalPrizeFromHost = messages.IntegerField(22)

    groupMembersOnly = messages.BooleanField(111)
    prizeDistributionType = messages.StringField(112)

    signupsStarted = messages.BooleanField(113)
    signupsFinished = messages.BooleanField(114)
    playStarted = messages.BooleanField(115)
    playFinished = messages.BooleanField(116)
    completed= messages.BooleanField(117)
    finalized= messages.BooleanField(118)

    #message = messages.StringField(19)

    resultDisplayText = messages.StringField(120)

    response_message = messages.StringField(1113)
    response_successful = messages.BooleanField(1114)

    teams = messages.MessageField(TeamResponse, 221, repeated=True)
    tiers = messages.MessageField(MatchCollection, 222, repeated=True)
    sponsors = messages.MessageField(TournamentSponsorResponse, 223, repeated=True)


class TournamentCollection(messages.Message):
    """ multiple Tournament """
    tournaments = messages.MessageField(TournamentResponse, 1, repeated=True)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)
