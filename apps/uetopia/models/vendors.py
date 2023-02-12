import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## we need proto rpc definitions for vendoritems
from apps.uetopia.models.vendor_items import VendorItemResponse
#from apps.leet.models.group_games import *
#from apps.leet.models.group_player_members import *

class Vendors(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    vendorTypeKeyId = ndb.IntegerProperty()
    vendorTypeTitle = ndb.StringProperty(indexed=False)

    developerUserKeyId = ndb.IntegerProperty()
    developerUserTitle = ndb.StringProperty(indexed=False)

    createdByUserKeyId = ndb.IntegerProperty()
    createdByUserTitle = ndb.StringProperty(indexed=False)
    createdByUserFirebaseUser = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    serverKeyId = ndb.IntegerProperty()
    serverTitle = ndb.StringProperty(indexed=False)

    buyingMax = ndb.IntegerProperty(indexed=False)
    sellingMax = ndb.IntegerProperty(indexed=False)

    costToBuy = ndb.IntegerProperty(indexed=False)
    transactionTaxPercentageToServer = ndb.FloatProperty(indexed=False)

    engineActorAsset = ndb.StringProperty(indexed=False)

    vendorCurrency = ndb.IntegerProperty(indexed=False) # how much does this server own - spendable or awardable

    ## Used by servers to know where to place
    coordLocationX = ndb.FloatProperty(indexed=False)
    coordLocationY = ndb.FloatProperty(indexed=False)
    coordLocationZ = ndb.FloatProperty(indexed=False)
    forwardVecX = ndb.FloatProperty(indexed=False)
    forwardVecY = ndb.FloatProperty(indexed=False)
    forwardVecZ = ndb.FloatProperty(indexed=False)

    buying = ndb.BooleanProperty(indexed=False)
    selling = ndb.BooleanProperty(indexed=False)

    discordWebhook = ndb.StringProperty(indexed=False)

    thisVendorDTID = ndb.IntegerProperty()


class VendorGetRequest(messages.Message):
    """ a match's key """
    key_id = messages.StringField(1)

VENDOR_GET_RESOURCE = endpoints.ResourceContainer(
    VendorGetRequest
)

class VendorCreateRequest(messages.Message):
    """ a Vendor """
    vendorTypeKeyId = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    serverKeyId = messages.IntegerField(5)
    buyingMax = messages.IntegerField(6, variant=messages.Variant.INT32)
    sellingMax = messages.IntegerField(7, variant=messages.Variant.INT32)
    costToBuy = messages.IntegerField(11, variant=messages.Variant.INT32)
    transactionTaxPercentageToServer = messages.FloatField(12)
    engineActorAsset = messages.StringField(13)
    thisVendorDTID = messages.IntegerField(14, variant=messages.Variant.INT32)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)


VENDOR_CREATE_RESOURCE = endpoints.ResourceContainer(
    VendorCreateRequest
)

class VendorEditRequest(messages.Message):
    """ a Vendor's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    serverKeyId = messages.IntegerField(5)
    buyingMax = messages.IntegerField(6, variant=messages.Variant.INT32)
    sellingMax = messages.IntegerField(7, variant=messages.Variant.INT32)
    costToBuy = messages.IntegerField(11, variant=messages.Variant.INT32)
    transactionTaxPercentageToServer = messages.FloatField(12)
    engineActorAsset = messages.StringField(13)

    discordWebhook = messages.StringField(14)

    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)

VENDOR_EDIT_RESOURCE = endpoints.ResourceContainer(
    VendorEditRequest
)

class VendorResponse(messages.Message):
    """ a Vendor's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    serverKeyId = messages.IntegerField(5)
    buyingMax = messages.IntegerField(6, variant=messages.Variant.INT32)
    sellingMax = messages.IntegerField(7, variant=messages.Variant.INT32)
    costToBuy = messages.IntegerField(11, variant=messages.Variant.INT32)
    transactionTaxPercentageToServer = messages.FloatField(12)
    engineActorAsset = messages.StringField(13)
    vendorCurrency = messages.IntegerField(14, variant=messages.Variant.INT32)
    discordWebhook = messages.StringField(15)
    items = messages.MessageField(VendorItemResponse, 45, repeated=True)
    bMyVendor = messages.BooleanField(51)
    vendorKeyIdStr = messages.StringField(60)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)



class VendorResponseCollectionPageRequest(messages.Message):
    """ a Vendor's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    serverKeyId = messages.IntegerField(5)

VENDOR_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    VendorResponseCollectionPageRequest
)

class VendorCollection(messages.Message):
    """ multiple Vendors """
    vendors = messages.MessageField(VendorResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
