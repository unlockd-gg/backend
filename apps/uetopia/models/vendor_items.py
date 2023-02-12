import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## we need proto rpc definitions for event, player and games
#from apps.leet.models.group_events import *
#from apps.leet.models.group_games import *
#from apps.leet.models.group_player_members import *

class VendorItems(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    vendorKeyId = ndb.IntegerProperty()
    vendorTitle = ndb.StringProperty(indexed=False)

    vendorTypeKeyId = ndb.IntegerProperty()
    vendorTypeTitle = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    serverKeyId = ndb.IntegerProperty()
    serverTitle = ndb.StringProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()  ## this is the vendor owner
    userTitle = ndb.StringProperty(indexed=False)
    firebaseUser = ndb.StringProperty(indexed=False)

    quantityAvailable = ndb.IntegerProperty()
    pricePerUnit = ndb.IntegerProperty()
    attributes = ndb.TextProperty(indexed=False)

    selling = ndb.BooleanProperty(indexed=True)

    buyingOffer = ndb.BooleanProperty(indexed=True)
    buyingOfferUserKeyId = ndb.IntegerProperty(indexed=True)
    buyingOfferUserTitle = ndb.StringProperty(indexed=False)
    buyingOfferFirebaseUser = ndb.StringProperty(indexed=False)
    buyingOfferExpires = ndb.DateTimeProperty()

    claimable = ndb.BooleanProperty(indexed=False)  # this item shows up in a players claim window
    claimableAsItem = ndb.BooleanProperty(indexed=True)  # this is an item that was offered for sale and rejected or expired
    claimableAsCurrency = ndb.BooleanProperty(indexed=True)  # this is an item that was offered for sale and purchased by the vendor owner
    claimableForUserKeyId = ndb.IntegerProperty(indexed=True)
    claimableForFirebaseUser = ndb.StringProperty(indexed=False)

    iconPath = ndb.StringProperty(indexed=False)
    blueprintPath = ndb.StringProperty(indexed=False)
    dataTableId = ndb.IntegerProperty()
    tier = ndb.IntegerProperty()



class VendorItemGetRequest(messages.Message):
    """ a match's key """
    key_id = messages.StringField(1)

VENDOR_ITEM_GET_RESOURCE = endpoints.ResourceContainer(
    VendorItemGetRequest
)

class VendorItemCreateRequest(messages.Message):
    """ a Vendor """
    vendorKeyId = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    vendorKeyId = messages.StringField(4)
    quantityAvailable = messages.IntegerField(5, variant=messages.Variant.INT32)
    pricePerUnit = messages.IntegerField(6, variant=messages.Variant.INT32)
    selling = messages.BooleanField(10)
    buyingOffer = messages.BooleanField(11)
    buyingOfferUserKeyId = messages.IntegerField(12, variant=messages.Variant.INT32)
    blueprintPath = messages.StringField(14)
    attributes = messages.StringField(15)
    dataTableId = messages.IntegerField(16, variant=messages.Variant.INT32)
    tier = messages.IntegerField(17, variant=messages.Variant.INT32)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)


VENDOR_ITEM_CREATE_RESOURCE = endpoints.ResourceContainer(
    VendorItemCreateRequest
)


class VendorItemResponse(messages.Message):
    """ a Vendor Item's data """
    key_id = messages.IntegerField(1)
    title = messages.StringField(2)
    description = messages.StringField(3)
    vendorKeyId = messages.IntegerField(4)
    quantityAvailable = messages.IntegerField(5, variant=messages.Variant.INT32)
    pricePerUnit = messages.IntegerField(6, variant=messages.Variant.INT32)
    selling = messages.BooleanField(10)
    buyingOffer = messages.BooleanField(11)
    buyingOfferUserKeyId = messages.IntegerField(12, variant=messages.Variant.INT32)
    buyingOfferExpires = messages.StringField(13) ## datetime
    key_id_str = messages.StringField(14)
    blueprintPath = messages.StringField(15)
    attributes = messages.StringField(16)
    dataTableId = messages.IntegerField(17, variant=messages.Variant.INT32)
    tier = messages.IntegerField(18, variant=messages.Variant.INT32)

    claimable = messages.BooleanField(21)
    claimableAsItem = messages.BooleanField(22)
    claimableAsCurrency = messages.BooleanField(23)

    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)



class VendorItemResponseCollectionPageRequest(messages.Message):
    """ a Vendor Item's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    vendorKeyId = messages.IntegerField(4)

VENDOR_ITEM_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    VendorItemResponseCollectionPageRequest
)

class VendorItemCollection(messages.Message):
    """ multiple Vendors """
    vendor_items = messages.MessageField(VendorItemResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
