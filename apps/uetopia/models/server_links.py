import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class ServerLinks(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    originServerKeyId = ndb.IntegerProperty()
    originServerTitle = ndb.StringProperty(indexed=False)

    serverClusterKeyId = ndb.IntegerProperty()
    serverClusterTitle = ndb.StringProperty(indexed=False)
    targetServerKeyId = ndb.IntegerProperty()
    targetServerTitle = ndb.StringProperty(indexed=False)

    targetStatusIsContinuous = ndb.BooleanProperty(indexed=False)
    targetStatusCreating = ndb.BooleanProperty(indexed=False)
    targetStatusProvisioned = ndb.BooleanProperty(indexed=False)
    targetStatusOnline = ndb.BooleanProperty(indexed=False)
    targetStatusFull = ndb.BooleanProperty(indexed=False)
    targetStatusDead = ndb.BooleanProperty(indexed=False)
    permissionCanMount = ndb.BooleanProperty(indexed=False)
    permissionCanUserTravel = ndb.BooleanProperty(indexed=False)
    permissionCanDismount = ndb.BooleanProperty(indexed=False)
    isEntryPoint = ndb.BooleanProperty(indexed=False)

    userKeyId = ndb.IntegerProperty()
    gameKeyId = ndb.IntegerProperty()

    resourcesUsedToTravel = ndb.StringProperty(indexed=False) ## Vespene, Magnacite, etc.
    resourceAmountsUsedToTravel = ndb.StringProperty(indexed=False) ## "20,300" we just hand off the string to the server to do with as they please.
    currencyCostToTravel = ndb.IntegerProperty(indexed=False)

    ## Used by servers to know where to place portals or travel controls
    coordLocationX = ndb.FloatProperty(indexed=False)
    coordLocationY = ndb.FloatProperty(indexed=False)
    coordLocationZ = ndb.FloatProperty(indexed=False)

    rotationX = ndb.FloatProperty(indexed=False)
    rotationY = ndb.FloatProperty(indexed=False)
    rotationZ = ndb.FloatProperty(indexed=False)

    hostConnectionLink = ndb.StringProperty(indexed=False)

    ## Server Instance Support
    targetInstanced = ndb.BooleanProperty(indexed=False)
    targetInstanceConfiguration = ndb.StringProperty(indexed=False)
    targetInstancePartySizeMaximum = ndb.IntegerProperty(indexed=False)

    ## Used by servers to know where to place the user the just travelled
    destinationLocationX = ndb.FloatProperty(indexed=False)
    destinationLocationY = ndb.FloatProperty(indexed=False)
    destinationLocationZ = ndb.FloatProperty(indexed=False)

    def to_json(self):
        return ({
            u'targetServerTitle': self.targetServerTitle,
            u'targetServerKeyId': str(self.targetServerKeyId),
            u'targetStatusIsContinuous': self.targetStatusIsContinuous,
            u'targetStatusCreating': self.targetStatusCreating,
            u'targetStatusProvisioned': self.targetStatusProvisioned,
            u'targetStatusOnline': self.targetStatusOnline,
            u'targetStatusFull': self.targetStatusFull,
            u'targetStatusDead': self.targetStatusDead,
            u'permissionCanMount': self.permissionCanMount,
            u'permissionCanUserTravel':self.permissionCanUserTravel,
            u'permissionCanDismount':self.permissionCanDismount,
            u'resourcesUsedToTravel':self.resourcesUsedToTravel or "",
            u'resourceAmountsUsedToTravel':self.resourceAmountsUsedToTravel or "",
            u'currencyCostToTravel':self.currencyCostToTravel,
            u'coordLocationX':self.coordLocationX,
            u'coordLocationY':self.coordLocationY,
            u'coordLocationZ':self.coordLocationZ,
            u'rotationX':self.rotationX,
            u'rotationY':self.rotationY,
            u'rotationZ':self.rotationZ,
            u'hostConnectionLink':self.hostConnectionLink or "",
            u'targetInstanced':self.targetInstanced,
            u'targetInstanceConfiguration':self.targetInstanceConfiguration,
            u'targetInstancePartySizeMaximum':self.targetInstancePartySizeMaximum
        })


class ServerLinkGetRequest(messages.Message):
    """ a match's key """
    key_id = messages.StringField(1)

SERVER_LINK_GET_RESOURCE = endpoints.ResourceContainer(
    ServerLinkGetRequest
)

class ServerLinkCreateRequest(messages.Message):
    """ a ServerLink """
    originServerKeyId = messages.IntegerField(1)
    permissionCanMount = messages.BooleanField(2)
    permissionCanUserTravel = messages.BooleanField(3)
    permissionCanDismount = messages.BooleanField(4)
    isEntryPoint = messages.BooleanField(5)
    serverClusterKeyId = messages.IntegerField(6)
    targetServerKeyId = messages.IntegerField(7)
    response_message = messages.StringField(8)
    resourcesUsedToTravel = messages.StringField(9)
    resourceAmountsUsedToTravel = messages.StringField(10)
    currencyCostToTravel = messages.IntegerField(11, variant=messages.Variant.INT32)
    coordLocationX = messages.FloatField(12)
    coordLocationY = messages.FloatField(13)
    coordLocationZ = messages.FloatField(14)
    rotationX = messages.FloatField(15)
    rotationY = messages.FloatField(16)
    rotationZ = messages.FloatField(17)
    destinationLocationX = messages.FloatField(20)
    destinationLocationY = messages.FloatField(21)
    destinationLocationZ = messages.FloatField(22)
    response_successful = messages.BooleanField(50)


SERVER_LINK_CREATE_RESOURCE = endpoints.ResourceContainer(
    ServerLinkCreateRequest
)

class ServerLinkEditRequest(messages.Message):
    """ a ServerLink's data """
    key_id = messages.IntegerField(1)
    originServerKeyId = messages.IntegerField(2)
    permissionCanMount = messages.BooleanField(3)
    permissionCanUserTravel = messages.BooleanField(4)
    permissionCanDismount = messages.BooleanField(5)
    isEntryPoint = messages.BooleanField(6)
    serverClusterKeyId = messages.IntegerField(7)
    targetServerKeyId = messages.IntegerField(8)
    response_message = messages.StringField(9)
    resourcesUsedToTravel = messages.StringField(10)
    resourceAmountsUsedToTravel = messages.StringField(11)
    currencyCostToTravel = messages.IntegerField(12, variant=messages.Variant.INT32)
    coordLocationX = messages.FloatField(13)
    coordLocationY = messages.FloatField(14)
    coordLocationZ = messages.FloatField(15)
    rotationX = messages.FloatField(16)
    rotationY = messages.FloatField(17)
    rotationZ = messages.FloatField(18)
    destinationLocationX = messages.FloatField(20)
    destinationLocationY = messages.FloatField(21)
    destinationLocationZ = messages.FloatField(22)
    targetStatusCreating = messages.BooleanField(43)
    targetStatusProvisioned = messages.BooleanField(44)
    targetStatusOnline = messages.BooleanField(45)
    response_successful = messages.BooleanField(50)

SERVER_LINK_EDIT_RESOURCE = endpoints.ResourceContainer(
    ServerLinkEditRequest
)

class ServerLinkResponse(messages.Message):
    """ a ServerLinks's data """
    key_id = messages.IntegerField(1)
    originServerKeyId = messages.IntegerField(2)
    permissionCanMount = messages.BooleanField(3)
    permissionCanUserTravel = messages.BooleanField(4)
    permissionCanDismount = messages.BooleanField(5)
    isEntryPoint = messages.BooleanField(6)
    serverClusterKeyId = messages.IntegerField(7)
    targetServerKeyId = messages.IntegerField(8)
    targetServerTitle = messages.StringField(9)
    resourcesUsedToTravel = messages.StringField(11)
    resourceAmountsUsedToTravel = messages.StringField(12)
    currencyCostToTravel = messages.IntegerField(13, variant=messages.Variant.INT32)
    coordLocationX = messages.FloatField(14)
    coordLocationY = messages.FloatField(15)
    coordLocationZ = messages.FloatField(16)
    rotationX = messages.FloatField(17)
    rotationY = messages.FloatField(18)
    rotationZ = messages.FloatField(19)
    gameKeyId = messages.IntegerField(20)
    originServerTitle = messages.StringField(30)
    serverClusterTitle = messages.StringField(31)
    destinationLocationX = messages.FloatField(40)
    destinationLocationY = messages.FloatField(41)
    destinationLocationZ = messages.FloatField(42)
    targetStatusCreating = messages.BooleanField(43)
    targetStatusProvisioned = messages.BooleanField(44)
    targetStatusOnline = messages.BooleanField(45)
    response_message = messages.StringField(47)
    response_successful = messages.BooleanField(50)



class ServerLinkResponseCollectionPageRequest(messages.Message):
    """ a server link's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    originServerKeyId = messages.IntegerField(4)

SERVER_LINK_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    ServerLinkResponseCollectionPageRequest
)

class ServerLinkCollection(messages.Message):
    """ multiple ServerLinks """
    server_links = messages.MessageField(ServerLinkResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(6)
    response_successful = messages.BooleanField(50)
