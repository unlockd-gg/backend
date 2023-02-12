import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Ads(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    gameModeKeyId = ndb.IntegerProperty()
    gameModeTitle = ndb.StringProperty(indexed=False)

    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty(indexed=False)

    groupGameKeyId = ndb.IntegerProperty()

    icon_url =  ndb.StringProperty(indexed=False)  # for display on the website

    textures =  ndb.StringProperty(indexed=False)  # for display in-game
    bid_per_impression = ndb.IntegerProperty(indexed=True) #how much to spend
    number_of_impressions = ndb.IntegerProperty(indexed=False) ## how many views are desired
    cost_total = ndb.IntegerProperty(indexed=False) ## calculated at the end to hold the actual amount
    cost_withdrawn = ndb.IntegerProperty(indexed=False) ## bid * impressions * 2 (allow for overage)
    currencyBalance = ndb.IntegerProperty(indexed=False) # how much does this ad own - each impression creates a transaction that depletes this

    count_shown = ndb.IntegerProperty(indexed=False) # how many times has this ad been shown

    submitted = ndb.BooleanProperty(indexed=False)
    approved = ndb.BooleanProperty(indexed=False)
    active = ndb.BooleanProperty(indexed=True) # primary bool to check
    rejected = ndb.BooleanProperty(indexed=False)
    rejection_message = ndb.StringProperty(indexed=False)

    refunded = ndb.BooleanProperty(indexed=False)
    finalized = ndb.BooleanProperty(indexed=True)


    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'title': self.title,
                u'description': self.description,
                u'icon_url':self.icon_url
        })

class AdResponse(messages.Message):
    """ an ad's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    created = messages.StringField(100) # DATETIME
    title = messages.StringField(101)
    description = messages.StringField(2)

    gameKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(4)

    gameModeKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    gameModeTitle = messages.StringField(6)

    groupKeyId = messages.IntegerField(7, variant=messages.Variant.INT32)
    groupTitle = messages.StringField(8)

    groupGameKeyId = messages.IntegerField(9, variant=messages.Variant.INT32)


    icon_url = messages.StringField(10)
    textures = messages.StringField(11)
    bid_per_impression = messages.IntegerField(12, variant=messages.Variant.INT32)
    number_of_impressions = messages.IntegerField(13, variant=messages.Variant.INT32)
    cost_total = messages.IntegerField(14, variant=messages.Variant.INT32)

    count_shown = messages.IntegerField(15, variant=messages.Variant.INT32)

    submitted = messages.BooleanField(21)
    approved =  messages.BooleanField(22)
    active = messages.BooleanField(23)
    rejected = messages.BooleanField(24)
    rejection_message = messages.StringField(25)

    refunded = messages.BooleanField(26)
    finalized = messages.BooleanField(27)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class AdRequest(messages.Message):
    """ an ad's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    title = messages.StringField(2)
    description = messages.StringField(3)

    gameKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(5)

    gameModeKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    gameModeTitle = messages.StringField(7)

    groupKeyId = messages.IntegerField(8, variant=messages.Variant.INT32)
    groupTitle = messages.StringField(9)

    groupGameKeyId = messages.IntegerField(10, variant=messages.Variant.INT32)

    icon_url = messages.StringField(100)
    textures = messages.StringField(101)
    bid_per_impression = messages.IntegerField(102, variant=messages.Variant.INT32)
    number_of_impressions = messages.IntegerField(103, variant=messages.Variant.INT32)
    cost_total = messages.IntegerField(104, variant=messages.Variant.INT32)

    count_shown = messages.IntegerField(105, variant=messages.Variant.INT32)

    submitted = messages.BooleanField(21)
    approved =  messages.BooleanField(22)
    active = messages.BooleanField(23)
    rejected = messages.BooleanField(24)
    rejection_message = messages.StringField(25)

AD_RESOURCE = endpoints.ResourceContainer(
    AdRequest
)

class AdsCollection(messages.Message):
    """ multiple ads """
    ads = messages.MessageField(AdResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class AdsCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.IntegerField(4)
    groupGameKeyId = messages.IntegerField(5)
    gameModeKeyId = messages.IntegerField(6)

ADS_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    AdsCollectionPageRequest
)
