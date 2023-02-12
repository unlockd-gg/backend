import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Vouchers(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    starts = ndb.DateTimeProperty()
    ends = ndb.DateTimeProperty()

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    offerKeyId = ndb.IntegerProperty()
    offerTitle = ndb.StringProperty(indexed=False)

    apiKey = ndb.StringProperty(indexed=True)

    singleUse = ndb.BooleanProperty(indexed=False)
    used = ndb.BooleanProperty(indexed=False)
    active = ndb.BooleanProperty(indexed=True)


    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description
        })

class VoucherResponse(messages.Message):
    """ a voucher's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    created = messages.StringField(100) # DATETIME
    starts = messages.StringField(101) # DATETIME
    ends = messages.StringField(102) # DATETIME

    title = messages.StringField(103)
    description = messages.StringField(2)

    gameKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(4)

    offerKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    offerTitle = messages.StringField(6)

    singleUse = messages.BooleanField(21)
    used =  messages.BooleanField(22)
    active = messages.BooleanField(23)

    apiKey = messages.StringField(104)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class VoucherRequest(messages.Message):
    """ a voucher's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    starts = messages.StringField(101) # DATETIME
    ends = messages.StringField(102) # DATETIME

    title = messages.StringField(103)
    description = messages.StringField(3)

    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(5)

    offerKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    offerTitle = messages.StringField(7)

    singleUse = messages.BooleanField(21)
    used =  messages.BooleanField(22)
    active = messages.BooleanField(23)

    autoRefresh = messages.BooleanField(30)
    apiKey = messages.StringField(104)


VOUCHER_RESOURCE = endpoints.ResourceContainer(
    VoucherRequest
)

class VoucherCollection(messages.Message):
    """ multiple vouchers """
    vouchers = messages.MessageField(VoucherResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class VoucherCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    offerKeyId = messages.IntegerField(5)

VOUCHER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    VoucherCollectionPageRequest
)
