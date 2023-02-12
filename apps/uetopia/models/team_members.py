import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class TeamMembers(ndb.Model):
    teamKeyId = ndb.IntegerProperty()
    teamTitle = ndb.StringProperty()
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty()
    userFirebaseUser = ndb.StringProperty()
    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty()
    gamePlayerKeyId = ndb.IntegerProperty()
    #playerAvatarTheme = ndb.StringProperty()
    invitedByUserKeyId = ndb.IntegerProperty()

    invited = ndb.BooleanProperty()
    joined = ndb.BooleanProperty()
    applicant = ndb.BooleanProperty()
    approved = ndb.BooleanProperty()
    captain = ndb.BooleanProperty()
    denied = ndb.BooleanProperty()

    order = ndb.IntegerProperty()

    nextTournamentKeyId = ndb.IntegerProperty()
    nextTournamentTitle = ndb.StringProperty()


    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                #u'playerAvatarTheme': self.playerAvatarTheme,
                u'invited': self.invited,
                u'joined': self.joined,
                u'applicant': self.applicant,
                u'approved': self.approved,
                u'captain': self.captain,
                u'denied': self.denied,
                u'order': self.order
        })

    def to_json_userKeyIdStr(self):
        return ({
                u'userKeyIdStr': str(self.userKeyId)
        })

class TeamPlayerMemberResponse(messages.Message):
    """ a Team player member's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    userKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    userTitle = messages.StringField(3)
    #playerAvatarTheme = messages.StringField(4)

    applicant = messages.BooleanField(5)
    joined = messages.BooleanField(6)
    approved = messages.BooleanField(16)
    captain = messages.BooleanField(17)
    denied = messages.BooleanField(18)
    order = messages.IntegerField(19)
    invited = messages.BooleanField(20)

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)

class TeamPlayerMemberUpdateRequest(messages.Message):
    """ a TeamPlayerMember's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    approved = messages.BooleanField(2)

TEAM_PLAYER_MEMBER_UPDATE_RESOURCE = endpoints.ResourceContainer(
    TeamPlayerMemberUpdateRequest
)
