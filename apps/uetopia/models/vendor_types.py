import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## we need proto rpc definitions for event, player and games
#from apps.leet.models.group_events import *
#from apps.leet.models.group_games import *
#from apps.leet.models.group_player_members import *

class VendorTypes(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    developerUserKeyId = ndb.IntegerProperty(indexed=False)
    developerUserTitle = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    buyingMax = ndb.IntegerProperty(indexed=False)
    sellingMax = ndb.IntegerProperty(indexed=False)

    costToBuy = ndb.IntegerProperty(indexed=False)
    transactionTaxPercentageToServer = ndb.FloatProperty(indexed=False)

    engineActorAsset = ndb.StringProperty(indexed=False)

    def to_json(self):
        return ({
            u'title': self.title,
            u'description': self.description,
            u'gameKeyId': self.gameKeyId,
            u'gameTitle': self.gameTitle,
            u'buyingMax': self.buyingMax,
            u'sellingMax': self.sellingMax,
            u'costToBuy': self.costToBuy,
            u'transactionTaxPercentageToServer': self.transactionTaxPercentageToServer,
            u'engineActorAsset': self.engineActorAsset
        })


class VendorTypeGetRequest(messages.Message):
    """ a match's key """
    key_id = messages.StringField(1)

VENDOR_TYPE_GET_RESOURCE = endpoints.ResourceContainer(
    VendorTypeGetRequest
)

class VendorTypeCreateRequest(messages.Message):
    """ a VendorType """
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    buyingMax = messages.IntegerField(6, variant=messages.Variant.INT32)
    sellingMax = messages.IntegerField(7, variant=messages.Variant.INT32)
    costToBuy = messages.IntegerField(11, variant=messages.Variant.INT32)
    transactionTaxPercentageToServer = messages.FloatField(12)
    engineActorAsset = messages.StringField(13)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)


VENDOR_TYPE_CREATE_RESOURCE = endpoints.ResourceContainer(
    VendorTypeCreateRequest
)

class VendorTypeEditRequest(messages.Message):
    """ a VendorType's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    buyingMax = messages.IntegerField(6, variant=messages.Variant.INT32)
    sellingMax = messages.IntegerField(7, variant=messages.Variant.INT32)
    costToBuy = messages.IntegerField(11, variant=messages.Variant.INT32)
    transactionTaxPercentageToServer = messages.FloatField(12)
    engineActorAsset = messages.StringField(13)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)

VENDOR_TYPE_EDIT_RESOURCE = endpoints.ResourceContainer(
    VendorTypeEditRequest
)

class VendorTypeResponse(messages.Message):
    """ a VendorType's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    buyingMax = messages.IntegerField(6, variant=messages.Variant.INT32)
    sellingMax = messages.IntegerField(7, variant=messages.Variant.INT32)
    costToBuy = messages.IntegerField(11, variant=messages.Variant.INT32)
    transactionTaxPercentageToServer = messages.FloatField(12)
    engineActorAsset = messages.StringField(13)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)



class VendorTypeResponseCollectionPageRequest(messages.Message):
    """ a VendorType's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)

VENDOR_TYPE_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    VendorTypeResponseCollectionPageRequest
)

class VendorTypeCollection(messages.Message):
    """ multiple ServerLinks """
    vendor_types = messages.MessageField(VendorTypeResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
