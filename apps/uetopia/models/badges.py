import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Badges(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    ends = ndb.DateTimeProperty()

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    offerKeyId = ndb.IntegerProperty()
    offerTitle = ndb.StringProperty(indexed=False)

    voucherKeyId = ndb.IntegerProperty()
    voucherTitle = ndb.StringProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)

    gamePlayerKeyId = ndb.IntegerProperty()
    #gamePlayerTitle = ndb.StringProperty(indexed=False)

    offerType = ndb.StringProperty(indexed=False)

    tags = ndb.StringProperty(repeated=True, indexed=False)

    icon_url = ndb.StringProperty(indexed=False)

    active = ndb.BooleanProperty(indexed=True)
    autoRefresh = ndb.BooleanProperty(indexed=False)


    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description
        })

class BadgeResponse(messages.Message):
    """ a badge's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    created = messages.StringField(100) # DATETIME
    ends = messages.StringField(102) # DATETIME

    title = messages.StringField(104)
    description = messages.StringField(2)

    gameKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(4)

    offerKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    offerTitle = messages.StringField(6)

    voucherKeyId = messages.IntegerField(7, variant=messages.Variant.INT32)
    voucherTitle = messages.StringField(8)

    offerType = messages.StringField(9)

    tags = messages.StringField(20, repeated=True)

    icon_url = messages.StringField(21)

    active = messages.BooleanField(24)
    autoRefresh = messages.BooleanField(25)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class BadgeRequest(messages.Message):
    """ a badge's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming

    autoRefresh = messages.BooleanField(24)


BADGE_RESOURCE = endpoints.ResourceContainer(
    BadgeRequest
)

class BadgeCollection(messages.Message):
    """ multiple badges """
    badges = messages.MessageField(BadgeResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class BadgeCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)

BADGE_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    BadgeCollectionPageRequest
)
