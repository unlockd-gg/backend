import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GameLevelLinks(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    gameLevelKeyId = ndb.IntegerProperty()
    gameLevelTitle = ndb.StringProperty(indexed=False)

    locationX = ndb.IntegerProperty(indexed=False)
    locationY = ndb.IntegerProperty(indexed=False)
    locationZ = ndb.IntegerProperty(indexed=False)
    selectionProbability = ndb.IntegerProperty(indexed=False)

    resourcesUsedToTravel = ndb.StringProperty(indexed=False) ## Vespene, Magnacite, etc.
    resourceAmountsUsedToTravel = ndb.StringProperty(indexed=False) ## "20,300" we just hand off the string to the server to do with as they please.
    currencyCostToTravel = ndb.IntegerProperty(indexed=False)

    isReturnLink = ndb.BooleanProperty(indexed=True)

    def to_json(self):
        return ({
                u'key_id': str(self.key.id())
        })

class GameLevelLinkResponse(messages.Message):
    """ a game level's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(2)
    gameTitle = messages.StringField(3)
    gameLevelKeyId = messages.IntegerField(4)
    gameLevelTitle = messages.StringField(5)
    selectionProbability = messages.IntegerField(6, variant=messages.Variant.INT32)
    locationX = messages.IntegerField(7, variant=messages.Variant.INT32)
    locationY = messages.IntegerField(8, variant=messages.Variant.INT32)
    locationZ = messages.IntegerField(9, variant=messages.Variant.INT32)

    resourcesUsedToTravel = messages.StringField(10)
    resourceAmountsUsedToTravel = messages.StringField(11)
    currencyCostToTravel = messages.IntegerField(12, variant=messages.Variant.INT32)

    isReturnLink = messages.BooleanField(13)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameLevelLinkRequest(messages.Message):
    """ a game level's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    gameKeyId = messages.IntegerField(2)
    gameTitle = messages.StringField(3)
    gameLevelKeyId = messages.IntegerField(4)
    gameLevelTitle = messages.StringField(5)
    selectionProbability = messages.IntegerField(6, variant=messages.Variant.INT32)
    locationX = messages.IntegerField(7, variant=messages.Variant.INT32)
    locationY = messages.IntegerField(8, variant=messages.Variant.INT32)
    locationZ = messages.IntegerField(9, variant=messages.Variant.INT32)

    resourcesUsedToTravel = messages.StringField(10)
    resourceAmountsUsedToTravel = messages.StringField(11)
    currencyCostToTravel = messages.IntegerField(12, variant=messages.Variant.INT32)

    isReturnLink = messages.BooleanField(13)


GAME_LEVEL_LINK_RESOURCE = endpoints.ResourceContainer(
    GameLevelLinkRequest
)


class GameLevelLinksCollection(messages.Message):
    """ multiple level links """
    game_level_links = messages.MessageField(GameLevelLinkResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameLevelLinksCollectionPageRequest(messages.Message):
    """ a levell collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    gameLevelKeyId = messages.IntegerField(5)

GAME_LEVEL_LINKS_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GameLevelLinksCollectionPageRequest
)
