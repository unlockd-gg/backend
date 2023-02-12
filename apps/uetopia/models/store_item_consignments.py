import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## we need proto rpc definitions for event, player and games
#from apps.leet.models.group_events import *
#from apps.leet.models.group_games import *
#from apps.leet.models.group_player_members import *

class StoreItemConsignments(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()  ## this is the user that created the item
    userTitle = ndb.StringProperty(indexed=False)

    group = ndb.BooleanProperty()
    groupKeyId = ndb.IntegerProperty()  ## this is the user that created the item
    groupTitle = ndb.StringProperty(indexed=False)

    pricePerUnit = ndb.IntegerProperty()



class StoreItemConsignmentRequest(messages.Message):
    """ a StoreItemConsignment's key """
    key_id = messages.StringField(1)

STORE_ITEM_CON_GET_RESOURCE = endpoints.ResourceContainer(
    StoreItemConsignmentRequest
)

class StoreItemConsignmentCreateRequest(messages.Message):
    """ a StoreItemConsignment """
    title = messages.StringField(1)
    description = messages.StringField(2)
    gameKeyId = messages.StringField(3)
    userKeyId = messages.StringField(4)
    group = messages.BooleanField(5)
    groupKeyId = messages.StringField(6)
    pricePerUnit = messages.IntegerField(7, variant=messages.Variant.INT32)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)


STORE_ITEM_CON_CREATE_RESOURCE = endpoints.ResourceContainer(
    StoreItemConsignmentCreateRequest
)


class StoreItemConsignmentResponse(messages.Message):
    """ a StoreItemConsignment's data """
    key_id = messages.IntegerField(1)
    created = messages.StringField(100) # DATETIME
    title = messages.StringField(2)
    description = messages.StringField(3)
    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(5)
    userKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    userTitle = messages.StringField(7)
    group = messages.BooleanField(8)
    groupKeyId = messages.IntegerField(9, variant=messages.Variant.INT32)
    groupTitle = messages.StringField(10)
    pricePerUnit = messages.IntegerField(11, variant=messages.Variant.INT32)
    response_message = messages.StringField(108)
    response_successful = messages.BooleanField(150)

STORE_ITEM_CON_EDIT_RESOURCE = endpoints.ResourceContainer(
    StoreItemConsignmentResponse
)

class StoreItemConsignmentCollectionPageRequest(messages.Message):
    """ a StoreItemConsignment's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)

STORE_ITEM_CON_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    StoreItemConsignmentCollectionPageRequest
)

class StoreItemConsignmentCollection(messages.Message):
    """ multiple StoreItemConsignment """
    store_item_cons = messages.MessageField(StoreItemConsignmentResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
