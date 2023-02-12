import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

from apps.uetopia.models.vm_base import VMBase

class Match(VMBase):

    allPlayersJoined = ndb.BooleanProperty()
    ## TODO determine which of these we can delete
    allPlayersCommitted = ndb.BooleanProperty()
    allPlayersApproved = ndb.BooleanProperty()
    allPlayersLeft = ndb.BooleanProperty()
    allPlayersVerified = ndb.BooleanProperty()
    allPlayersReportedFailure = ndb.BooleanProperty()

    matchVerified = ndb.BooleanProperty()
    matchExpired = ndb.BooleanProperty()

    public = ndb.BooleanProperty()

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)

    iconServingUrl = ndb.StringProperty(indexed=False)
    bannerServingUrl = ndb.StringProperty(indexed=False)
    cssServingUrl = ndb.StringProperty(indexed=False)

    playersPerTeam = ndb.IntegerProperty(indexed=False)
    teams = ndb.IntegerProperty(indexed=False)

    map_title = ndb.StringProperty(indexed=False)
    map_id = ndb.StringProperty(indexed=False)

    gameModeKeyId = ndb.IntegerProperty(indexed=False)
    gameModeTitle = ndb.StringProperty(indexed=False)

    admissionFeePerPlayer = ndb.IntegerProperty(indexed=False)
    winRewardPerPlayer = ndb.IntegerProperty(indexed=False)


    ## ADDITIONS TO SUPPORT TOURNAMENTS
    tournamentKeyId = ndb.IntegerProperty()
    tournamentTitle = ndb.StringProperty(indexed=False)
    tournamentTier = ndb.IntegerProperty(indexed=True)
    tournamentMatchNumber = ndb.IntegerProperty(indexed=False)

    tournamentTeamKeyId1 = ndb.IntegerProperty()
    tournamentTeamTitle1 = ndb.StringProperty(indexed=False)
    tournamentTeamKeyId2 = ndb.IntegerProperty()
    tournamentTeamTitle2 = ndb.StringProperty(indexed=False)
    tournamentMatchWinnerKeyId = ndb.IntegerProperty()
    tournamentMatchLoserKeyId = ndb.IntegerProperty()

    ## VM specific stuff
    match_creating = ndb.BooleanProperty(indexed=False)
    match_creating_timestamp = ndb.DateTimeProperty(indexed=False)
    match_provisioned = ndb.BooleanProperty(indexed=True)
    match_active = ndb.BooleanProperty(indexed=False)
    match_title = ndb.StringProperty(indexed=False) ## the title of the VM instnace.  Matches are just the keyID with an "m" in front
    match_entry = ndb.BooleanProperty(indexed=True)

    match_destroying = ndb.BooleanProperty(indexed=False)
    match_destroying_timestamp = ndb.DateTimeProperty(indexed=False)

    ## metagame additions
    metaMatchKeyId = ndb.IntegerProperty(indexed=False)
    ## Match specific info from the metagame backend
    metaMatchTravelUrl = ndb.StringProperty(indexed=False)
    metaMatchCustom = ndb.TextProperty(indexed=False) # JSON additional details about the match - defenses, upgrades etc.



    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'allPlayersJoined': self.allPlayersJoined,
                u'allPlayersCommitted': self.allPlayersCommitted,
                u'allPlayersApproved': self.allPlayersApproved,
                u'allPlayersVerified': self.allPlayersVerified,
                u'public': self.public,
                u'admissionFee': self.admissionFee,
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                u'playersPerTeam':self.playersPerTeam,
                u'teams': self.teams,
                u'tournamentTeamTitle1': self.tournamentTeamTitle1,
                u'tournamentTeamTitle2':self.tournamentTeamTitle2
        })

    def to_json_tournament_view(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'allPlayersJoined': self.allPlayersJoined,
                u'allPlayersCommitted': self.allPlayersCommitted,
                u'allPlayersApproved': self.allPlayersApproved,
                u'allPlayersVerified': self.allPlayersVerified,
                u'public': self.public,
                u'admissionFee': self.admissionFee,
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                u'playersPerTeam':self.playersPerTeam,
                u'teams': self.teams,
                u'tournamentTeamTitle1': self.tournamentTeamTitle1,
                u'tournamentTeamTitle2':self.tournamentTeamTitle2,
                u'TournamentTeam1Winner': self.TournamentTeam1Winner,
                u'TournamentTeam1Loser':self.TournamentTeam1Loser,
                u'TournamentTeam2Winner':self.TournamentTeam2Winner,
                u'TournamentTeam2Loser':self.TournamentTeam2Loser
        })
### PROTORPC MODELS FOR ENDPOINTS

class MatchGetRequest(messages.Message):
    """ a match's key """
    aekey = messages.StringField(1)

MATCH_GET_RESOURCE = endpoints.ResourceContainer(
    MatchGetRequest
)

class MatchCreateRequest(messages.Message):
    """ a match's key """
    gameKey = messages.StringField(1)
    groupKey = messages.StringField(2)
    title = messages.StringField(3)
    wager = messages.IntegerField(4)

    playerMin = messages.IntegerField(5)
    playerMax = messages.IntegerField(6)
    teamsize = messages.IntegerField(7)

    mapConfiguration = messages.StringField(8)
    public = messages.BooleanField(9)

    groupmatch = messages.BooleanField(10)


MATCH_CREATE_RESOURCE = endpoints.ResourceContainer(
    MatchCreateRequest
)

class MatchResponse(messages.Message):
    """ a match's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)

    allPlayersJoined = messages.BooleanField(4)
    allPlayersCommitted = messages.BooleanField(5)
    allPlayersApproved = messages.BooleanField(6)
    allPlayersLeft = messages.BooleanField(7)
    allPlayersVerified = messages.BooleanField(8)
    allPlayersReportedFailure = messages.BooleanField(9)

    gameJoinLink = messages.StringField(10)
    wagerPerPlayerSatoshi = messages.IntegerField(11)
    playerMin = messages.IntegerField(12)
    playerMax = messages.IntegerField(13)

    playersCurrent = messages.IntegerField(14)

    password = messages.StringField(15)

    message = messages.StringField(17)

    iconServingUrl = messages.StringField(18)
    gameTitle = messages.StringField(19)
    gameKey = messages.StringField(20)

    map_title = messages.StringField(21)

    wager_per_player_minimum = messages.IntegerField(22)
    wager_per_player_maximum = messages.IntegerField(23)

    tournamentTeamTitle1 = messages.StringField(24)
    tournamentTeamTitle2 = messages.StringField(25)

    tournamentTeamKeyId1 = messages.StringField(26)
    tournamentTeamKeyId2 = messages.StringField(27)

    TournamentTeam1Winner = messages.BooleanField(31)
    TournamentTeam1Loser = messages.BooleanField(32)
    TournamentTeam2Winner = messages.BooleanField(33)
    TournamentTeam2Loser = messages.BooleanField(34)


    ##players = messages.MessageField(MatchPlayerResponse, 26, repeated=True)


class MatchResponseUnderscores(messages.Message):
    """ a match's data """
    key = messages.StringField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)

    all_players_joined = messages.BooleanField(4)
    all_players_committed = messages.BooleanField(5)
    all_players_approved = messages.BooleanField(6)
    all_players_left = messages.BooleanField(7)
    all_players_verified = messages.BooleanField(8)
    all_players_reported_failure = messages.BooleanField(9)

    game_join_link = messages.StringField(10)
    wager_per_player_satoshi = messages.IntegerField(11)
    player_min = messages.IntegerField(12)
    player_max = messages.IntegerField(13)
    players_current = messages.IntegerField(14)

    password = messages.StringField(15)

    message = messages.StringField(17)

    icon_serving_url = messages.StringField(18)
    game_title = messages.StringField(19)
    game_key = messages.StringField(20)

    map_title = messages.StringField(21)

    wager_per_player_minimum = messages.IntegerField(22)
    wager_per_player_maximum = messages.IntegerField(23)




class MatchCollection(messages.Message):
    """ multiple matches """
    matches = messages.MessageField(MatchResponse, 1, repeated=True)
    tier = messages.IntegerField(2)
