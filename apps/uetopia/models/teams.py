import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

#from apps.leet.models.team_player_members import *

class Teams(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty()
    description = ndb.TextProperty()
    pug = ndb.BooleanProperty() ## these get purged after a tournament is complete
    teamAvatarTheme = ndb.StringProperty()

    #platformKey = ndb.StringProperty()
    #platformTitle = ndb.StringProperty()

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty()

    groupMembersOnly = ndb.BooleanProperty()
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()

    captainPlayerKeyId = ndb.IntegerProperty()
    captainPlayerTitle = ndb.StringProperty()

    nextPlayStartTime = ndb.DateTimeProperty()
    nextPlayEndTime = ndb.DateTimeProperty()
    nextMatchKeyId = ndb.IntegerProperty()
    nextMatchTitle = ndb.StringProperty()

    nextTournamentStartTime = ndb.DateTimeProperty()
    nextTournamentEndTime = ndb.DateTimeProperty()
    nextTournamentKeyId = ndb.IntegerProperty()
    nextTournamentTitle = ndb.StringProperty()
    nextTournamentEliminated = ndb.BooleanProperty()

    teamSizeMax = ndb.IntegerProperty()
    teamSizeCurrent = ndb.IntegerProperty()
    teamFull = ndb.BooleanProperty()

    ## State flags
    initialized = ndb.BooleanProperty()
    recruiting = ndb.BooleanProperty()
    inTournament = ndb.BooleanProperty()
    activeInTournament = ndb.BooleanProperty()
    inMatch = ndb.BooleanProperty()
    purged = ndb.BooleanProperty()

    ## Integrations
    slack_webhook = ndb.StringProperty(indexed=False)
    slack_subscribe_tournaments = ndb.BooleanProperty(indexed=False)
    slack_subscribe_errors = ndb.BooleanProperty(indexed=False)
    slack_subscribe_matches = ndb.BooleanProperty(indexed=False)
    slack_subscribe_config_changes = ndb.BooleanProperty(indexed=False)
    slack_subscribe_new_users = ndb.BooleanProperty(indexed=False)

    discord_webhook = ndb.StringProperty(indexed=False)
    discord_subscribe_tournaments = ndb.BooleanProperty(indexed=False)
    discord_subscribe_errors = ndb.BooleanProperty(indexed=False)
    discord_subscribe_matches = ndb.BooleanProperty(indexed=False)
    discord_subscribe_config_changes = ndb.BooleanProperty(indexed=False)
    discord_subscribe_new_users = ndb.BooleanProperty(indexed=False)

    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'teamAvatarTheme': self.teamAvatarTheme,
                u'purged':self.purged,
                u'teamSizeMax': self.teamSizeMax,
                u'teamSizeMaxStr': str(self.teamSizeMax), ## Unreal has an easier time with strings.
        })

    def to_json_with_UserIds(self):
        ## This is used in the UE OSS for team invitations
        ## Ids are passed as strings because that's how UE deals with them.
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'userKeyId': str(self.userKeyId),
                u'senderKeyId': str(self.senderKeyId),
                u'senderUserTitle':self.senderUserTitle
        })

    def to_json_with_members(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'teamAvatarTheme': self.teamAvatarTheme,
                u'members': self.members,
                u'teamSizeMax': self.teamSizeMax,
                u'teamSizeMaxStr': str(self.teamSizeMax), ## Unreal has an easier time with strings.
                u'teamSizeCurrent': self.teamSizeCurrent,
                u'teamFull': self.teamFull,
                u'recruiting':self.recruiting,
                u'userIsCaptain':self.userIsCaptain ## sent so that captains can be identified

        })


### PROTORPC MODELS FOR ENDPOINTS

class TeamGetRequest(messages.Message):
    """ a Team's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    teamKeyIdStr = messages.StringField(2) ## the UE client can't send this as an int for some reason
    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameKeyIdStr = messages.StringField(7) ## the UE client can't send this as an int for some reason
    userKeyId = messages.IntegerField(14, variant=messages.Variant.INT32)
    userKeyIdStr = messages.StringField(17) ## the UE client can't send this as an int for some reason

TEAM_GET_RESOURCE = endpoints.ResourceContainer(
    TeamGetRequest
)

class TeamCreateRequest(messages.Message):
    """ a Team's data """
    tournamentKeyId = messages.IntegerField(1, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    title = messages.StringField(3)
    description = messages.StringField(4)
    teamSize = messages.IntegerField(5, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    gameKeyIdStr = messages.StringField(7) ## the UE client can't send this as an int for some reason
    groupMembersOnly = messages.BooleanField(10)

TEAM_CREATE_RESOURCE = endpoints.ResourceContainer(
    TeamCreateRequest
)

class TeamResponse(messages.Message):
    """ a Team's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    teamSizeMax = messages.IntegerField(4)
    teamSizeCurrent = messages.IntegerField(5)
    teamFull = messages.BooleanField(6)
    initialized = messages.BooleanField(7)
    recruiting = messages.BooleanField(8)
    inTournament = messages.BooleanField(9)
    inMatch = messages.BooleanField(10)
    message = messages.StringField(11)
    player_is_captain = messages.BooleanField(12)
    player_is_member = messages.BooleanField(13)
    #members = messages.MessageField(TeamPlayerMemberResponse, 14, repeated=True)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)

class TeamCollectionPageRequest(messages.Message):
    """ a team's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameKeyIdStr = messages.StringField(7) ## the UE client can't send this as an int for some reason

TEAM_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    TeamCollectionPageRequest
)


class TeamCollection(messages.Message):
    """ multiple Teams """
    teams = messages.MessageField(TeamResponse, 1, repeated=True)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)
