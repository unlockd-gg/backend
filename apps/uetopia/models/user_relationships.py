import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class UserRelationships(ndb.Model):
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty(indexed=False)
    userFirebaseUser = ndb.StringProperty(indexed=False)
    userTargetKeyId = ndb.IntegerProperty()
    userTargetTitle = ndb.StringProperty(indexed=False)
    userTargetFirebaseUser = ndb.StringProperty(indexed=False)
    friend = ndb.BooleanProperty()
    friendConfirmed = ndb.BooleanProperty()
    ignore = ndb.BooleanProperty(indexed=False)
    nickname = ndb.StringProperty(indexed=False)
    userTargetPicture = ndb.StringProperty(indexed=False)
    online = ndb.BooleanProperty()
    playingGame = ndb.StringProperty(indexed=False)
    playingGameKeyId = ndb.IntegerProperty(indexed=False)
    playingOnServer = ndb.StringProperty(indexed=False)
    playingOnServerKeyId = ndb.IntegerProperty(indexed=False)

    def to_json(self):
        return ({
            u'userTargetKeyId': self.userTargetKeyId,
            u'key_id': self.key.id(),
            u'userTargetTitle': self.userTargetTitle,
            u'userTargetPicture': self.userTargetPicture,
            u'online': self.online,
            u'friend': self.friend,
            u'friendConfirmed': self.friendConfirmed,
            u'nickname': self.nickname,
            })

    def to_json_with_status(self):
        return ({
            u'userTargetKeyId': self.userTargetKeyId,
            u'key_id': self.key.id(),
            u'userTargetTitle': self.userTargetTitle,
            u'userTargetPicture': self.userTargetPicture,
            u'online': self.online,
            u'friend': self.friend,
            u'friendConfirmed': self.friendConfirmed,
            u'nickname': self.nickname,
            u'playingGame': self.playingGame,
            u'playingOnServer': self.playingOnServer,
            u'playingLink': self.playingLink,
            u'streaming':self.streaming,
            u'streamLink':self.streamLink
            })

    def to_json_ue_oss_format(self):
        return ({
            #u'UserId': self.userTargetKeyId,
            u'key_id': self.userTargetKeyId,
            u'username': self.userTargetTitle,
            #u'userTargetPicture': self.userTargetPicture,
            u'online': self.online,
            #u'friend': self.friend,
            #u'friendConfirmed': self.friendConfirmed,
            #u'nickname': self.nickname,
            u'playingGame': self.playingGame,
            u'playingOnServer': self.playingOnServer,
            #u'playingLink': self.playingLink,
            #u'streaming':self.streaming,
            #u'streamLink':self.streamLink
            })


class UserRelationshipCreateRequest(messages.Message):
    """ create a UserRelationship """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    friend = messages.BooleanField(2)
    ignore = messages.BooleanField(3)
    nickname = messages.StringField(4)


USER_RELATIONSHIP_CREATE_RESOURCE = endpoints.ResourceContainer(
    UserRelationshipCreateRequest
)

class UserRelationshipGetResponse(messages.Message):
    """ a UserRelationship's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    userTargetKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    userTargetTitle = messages.StringField(3)
    friend = messages.BooleanField(4)
    friendConfirmed = messages.BooleanField(5)
    ignore = messages.BooleanField(6)
    nickname = messages.StringField(7)
    #message = messages.StringField(8)
    updated = messages.BooleanField(9)
    userTargetKeyIdStr = messages.StringField(10)
    relationship_exists = messages.BooleanField(39)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)

class UserRelationshipCollection(messages.Message):
    """ multiple relationships """
    online = messages.MessageField(UserRelationshipGetResponse, 1, repeated=True)
    offline = messages.MessageField(UserRelationshipGetResponse, 2, repeated=True)
    more = messages.BooleanField(3)
    cursor = messages.StringField(4)
    sort_order = messages.StringField(5)
    direction = messages.StringField(6)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)

class UserRelationshipCollectionPageRequest(messages.Message):
    """ a BountySummaries page request """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    gameKeyId = messages.StringField(4)

USER_RELATIONSHIPS_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    UserRelationshipCollectionPageRequest
)

class UserRelationshipGetResponseOSS(messages.Message):
    """ a UserRelationship's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    userTargetKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    userTargetTitle = messages.StringField(3)
    friend = messages.BooleanField(4)
    friendConfirmed = messages.BooleanField(5)
    ignore = messages.BooleanField(6)
    username = messages.StringField(7)
    #message = messages.StringField(8)
    updated = messages.BooleanField(9)
    bIsPlayingThisGame = messages.BooleanField(10)
    bIsOnline = messages.BooleanField(11)
    keyIdStr = messages.StringField(20) ## UE does not like Integer keys
    relationship_exists = messages.BooleanField(39)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)

class UserRelationshipCollectionOSS(messages.Message):
    """ multiple relationships """
    data = messages.MessageField(UserRelationshipGetResponseOSS, 1, repeated=True)
    more = messages.BooleanField(3)
    cursor = messages.StringField(4)
    sort_order = messages.StringField(5)
    direction = messages.StringField(6)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)
