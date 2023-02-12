import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Offers(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    duration_days = ndb.IntegerProperty()
    duration_seconds = ndb.IntegerProperty()

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    offerType = ndb.StringProperty(indexed=False)

    price = ndb.IntegerProperty(indexed=False)

    tags = ndb.StringProperty(repeated=True, indexed=False)

    icon_url = ndb.StringProperty(indexed=False)

    requireVoucher = ndb.BooleanProperty(indexed=False)
    visible = ndb.BooleanProperty(indexed=True)
    active = ndb.BooleanProperty(indexed=True)

    timed = ndb.BooleanProperty(indexed=False)
    autoRefreshCapable = ndb.BooleanProperty(indexed=False)


    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'tags': self.tags,
                u'icon_url': self.icon_url,
                u'price': self.price,
                u'offerType': self.offerType
        })

class OfferResponse(messages.Message):
    """ an offer's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    created = messages.StringField(100) # DATETIME
    title = messages.StringField(101)
    description = messages.StringField(2)

    gameKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(4)

    offerType = messages.StringField(5)

    tags = messages.StringField(7, repeated=True)

    icon_url = messages.StringField(8)
    price = messages.IntegerField(9, variant=messages.Variant.INT32)

    requireVoucher = messages.BooleanField(21)
    visible =  messages.BooleanField(22)
    active = messages.BooleanField(23)
    timed = messages.BooleanField(24)
    autoRefreshCapable = messages.BooleanField(25)

    duration_days = messages.IntegerField(30, variant=messages.Variant.INT32)
    duration_seconds = messages.IntegerField(31, variant=messages.Variant.INT32)

    existingBadge = messages.BooleanField(32)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class OfferRequest(messages.Message):
    """ an offer's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    title = messages.StringField(2)
    description = messages.StringField(3)

    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(5)

    offerType = messages.StringField(6)
    tags = messages.StringField(7, repeated=True)

    icon_url = messages.StringField(8)
    price = messages.IntegerField(9, variant=messages.Variant.INT32)

    requireVoucher = messages.BooleanField(21)
    visible =  messages.BooleanField(22)
    active = messages.BooleanField(23)
    timed = messages.BooleanField(24)
    autoRefreshCapable = messages.BooleanField(25)

    duration_days = messages.IntegerField(30, variant=messages.Variant.INT32)
    duration_seconds = messages.IntegerField(31, variant=messages.Variant.INT32)

    voucherKey = messages.StringField(60)
    existingBadge = messages.BooleanField(61)

    autoRefresh = messages.BooleanField(90)


OFFER_RESOURCE = endpoints.ResourceContainer(
    OfferRequest
)

class OfferCollection(messages.Message):
    """ multiple offers """
    offers = messages.MessageField(OfferResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class OfferCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)

OFFER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    OfferCollectionPageRequest
)
