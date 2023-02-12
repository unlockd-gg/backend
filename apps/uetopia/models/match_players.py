import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class MatchPlayers(ndb.Model):
    """ a connection between a player and a Match.  Used in matchmaker to track the status of each player.


    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    userKeyId = ndb.IntegerProperty(indexed=True)
    userTitle = ndb.StringProperty(indexed=False)
    firebaseUser = ndb.StringProperty(indexed=False)
    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)
    gamePlayerKeyId = ndb.IntegerProperty(indexed=False)
    matchKeyId = ndb.IntegerProperty(indexed=True)  ## these will not exist when a player is pending matchmaker
    matchTitle = ndb.StringProperty(indexed=False) ## these will not exist when a player is pending matchmaker


    teamId = ndb.IntegerProperty() # may be used externally to indicate team
    teamKeyId = ndb.IntegerProperty() # our internal team reference
    teamTitle = ndb.StringProperty(indexed=False)
    defaultTeamTitle = ndb.StringProperty(indexed=False) # copied in from user record on matchmaker start

    matchTeamKeyId = ndb.IntegerProperty(indexed=True) # link back to the match_team
    matchTeamTitle = ndb.StringProperty(indexed=False)

    groupTag = ndb.StringProperty(indexed=False) # copied in from user record on matchmaker start
    groupTagKeyId = ndb.IntegerProperty(indexed=False) # copied in from user record on matchmaker start

    win = ndb.BooleanProperty()
    teamCaptain = ndb.BooleanProperty()

    ## TODO - identify the flags we're not using and delete them.
    joined = ndb.BooleanProperty()
    committed = ndb.BooleanProperty()
    approved = ndb.BooleanProperty()
    left = ndb.BooleanProperty()
    verified = ndb.BooleanProperty()
    blocked = ndb.BooleanProperty()

    matchmaker_team_assignment_in_progress = ndb.BooleanProperty()

    ## matchmaker stuff
    matchmakerStarted = ndb.BooleanProperty(indexed=True)
    matchmakerPending = ndb.BooleanProperty(indexed=True)  # show up in the task list
    matchTaskStatusKeyId = ndb.IntegerProperty()
    matchmakerFoundMatch = ndb.BooleanProperty(indexed=True) # matchmaker created a match and assigned this player to it.
    matchmakerServerReady = ndb.BooleanProperty(indexed=False) # the server has checked in, and is ready for players.
    matchmakerJoinPending = ndb.BooleanProperty(indexed=True)  # true until the match is complete.
    matchmakerJoinable = ndb.BooleanProperty(indexed=True) # matchmaker created a match and assigned this player to it.
    matchmakerCheckUnusedProcessed = ndb.BooleanProperty(indexed=False)
    matchmakerFinished = ndb.BooleanProperty(indexed=False)
    matchmakerMode = ndb.StringProperty(indexed=False)

    matchmakerPaidAdmission = ndb.BooleanProperty(indexed=False)

    matchmakerUserRegion = ndb.StringProperty(indexed=False)

    # track for debugging / analysis
    rank = ndb.IntegerProperty(indexed=False)
    score = ndb.IntegerProperty(indexed=False)
    experience = ndb.IntegerProperty(indexed=False)

    # match results player copied over
    # we don't need it anymore

    playstyle_killer = ndb.IntegerProperty(indexed=False)
    playstyle_achiever = ndb.IntegerProperty(indexed=False)
    playstyle_explorer = ndb.IntegerProperty(indexed=False)
    playstyle_socializer = ndb.IntegerProperty(indexed=False)
    hero = ndb.StringProperty(indexed=False)
    weapon = ndb.StringProperty(indexed=False)
    #postiveCount = ndb.IntegerProperty(indexed=False)
    #negativeCount = ndb.IntegerProperty(indexed=False)
    killedUserKeyIDs = ndb.IntegerProperty(repeated=True, indexed=False)  ## the identifier we have right away
    killedUserTitles = ndb.StringProperty(repeated=True, indexed=False) ## to fill in later if we need it

    # ue session stuff
    session_host_address = ndb.StringProperty(indexed=False)
    session_id = ndb.StringProperty(indexed=False)

    # The UE server needs to know in advance if this player has already set up the character.
    ## this will get set when matchmaker start is run
    characterCustomized = ndb.BooleanProperty(indexed=False)

    ## pass twitch stream information so it can be shown in game
    twitch_channel_id = ndb.StringProperty(indexed=False)
    twitch_currently_streaming = ndb.BooleanProperty(indexed=False)

    stale = ndb.DateTimeProperty(indexed=True)
    stale_requires_check = ndb.BooleanProperty(indexed=True)

    def to_json(self):

        return ({
                u'key_id': str(self.key.id()),
                u'userKeyId': str(self.userKeyId),
                u'userTitle':self.userTitle,
                u'matchKeyId': self.matchKeyId,
                u'joined': self.joined,
                u'committed': self.committed,
                u'approved': self.approved,
                u'verified': self.verified,
                #u'isHost': self.isHost,
                u'blocked': self.blocked,
                u'teamId':self.teamId,
                u'teamKeyId': self.teamKeyId,
                u'teamTitle': self.teamTitle,
                u'rank': self.rank,
                u'score': self.score,
                u'gamePlayerKeyId': self.gamePlayerKeyId,
                u'characterCustomized': self.characterCustomized,
                u'twitchCurrentlyStreaming': self.twitch_currently_streaming,
                u'twitchChannelId': self.twitch_channel_id
                ## u'platformId': self.platformAlternateId,  ## do not send this, as it goes out to all players.
        })
