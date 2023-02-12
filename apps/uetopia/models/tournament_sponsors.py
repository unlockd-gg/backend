import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class TournamentSponsors(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    tournamentKeyId = ndb.IntegerProperty()
    tournamentTitle = ndb.StringProperty()

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)
    groupIconUrl = ndb.StringProperty(indexed=False)  ## for web front facing

    hostUserKeyId = ndb.IntegerProperty()
    hostUserTitle = ndb.StringProperty(indexed=False)

    inGameTextureServingUrl = ndb.StringProperty()  ## this is copied from group_game for easy access.


    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'title': self.title,
                u'gameKeyId': self.gameKeyId,
                u'gameTitle': self.gameTitle,
                u'groupKeyId': self.groupKeyId,
                u'groupTitle':self.groupTitle,
                u'groupIconUrl':self.groupIconUrl,
                u'hostUserKeyId':self.hostUserKeyId
        })

### PROTORPC MODELS FOR ENDPOINTS

class TournamentSponsorGetRequest(messages.Message):
    """ a Tournament's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    keyIdStr = messages.StringField(2) ## STR if it's coming from UE clients
    gameKeyIdStr = messages.StringField(5) ## STR if it's coming from UE clients


TOURNAMENT_SPONSOR_GET_RESOURCE = endpoints.ResourceContainer(
    TournamentSponsorGetRequest
)

class TournamentSponsorCreateRequest(messages.Message):
    """ a Tournament Sponsor's data """
    gameKeyId = messages.IntegerField(1, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    tournamentKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    title = messages.StringField(13)
    description = messages.StringField(14)
    groupTag = messages.StringField(111)

TOURNAMENT_SPONSOR_CREATE_RESOURCE = endpoints.ResourceContainer(
    TournamentSponsorCreateRequest
)

class TournamentSponsorResponse(messages.Message):
    """ a Tournament's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    keyIdStr = messages.StringField(2) ## STR if it's coming from UE clients
    title = messages.StringField(12)
    description = messages.StringField(13)
    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    groupIconUrl = messages.StringField(14)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)

class TournamentSponsorCollection(messages.Message):
    """ multiple Tournament Sponsors"""
    sponsors = messages.MessageField(TournamentSponsorResponse, 1, repeated=True)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)
