import endpoints
import datetime
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GameData(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)

    # Firebase auth
    firebaseUser = ndb.StringProperty(indexed=False)

    customKey = ndb.StringProperty(indexed=False)
    ## Arbitrary text that servers can use to retrieve and store common information about a user
    data = ndb.TextProperty(indexed=False)

    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'customKey': self.customKey,
        })


class GameDataResponse(messages.Message):
    """ a game data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(3)
    customKey = messages.StringField(4)
    data = messages.StringField(5)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameDataRequest(messages.Message):
    """ a game data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(3)
    customKey = messages.StringField(4)
    data = messages.StringField(5)


GAME_DATA_RESOURCE = endpoints.ResourceContainer(
    GameDataRequest
)


class GameDataCollection(messages.Message):
    """ multiple game datas """
    game_data = messages.MessageField(GameDataResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class GameDataCollectionPageRequest(messages.Message):
    """ a data collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)

GAME_DATA_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    GameDataCollectionPageRequest
)
