import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class ChatChannelSubscribers(ndb.Model):
    """ a chat channel subscriber.
    can contain data and/or text

    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    ## TODO - these should deleted out on a regular basis if stale.

    online = ndb.BooleanProperty()

    chatChannelKeyId = ndb.IntegerProperty()
    chatChannelTitle = ndb.StringProperty()
    chatChannelRefKeyId = ndb.IntegerProperty()
    channel_type = ndb.StringProperty()

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty()
    userFirebaseUser = ndb.StringProperty()

    chatChannelOwnerKeyId = ndb.IntegerProperty()

    post_count = ndb.IntegerProperty()

    def to_json(self):
        return ({
                u'key': self.key.urlsafe(),
                u'online': self.online,
                u'chatChannelKey': self.chatChannelKey,
                u'chatChannelTitle': self.chatChannelTitle,
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                u'post_count': self.post_count,
                u'channel_type': self.channel_type,
                u'chatChannelRefKey': self.chatChannelRefKey
        })


class ChatChanelSubscriberGetResponse(messages.Message):
    """ a ChatChannelSubscriber's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    key_id_str = messages.StringField(2)

    chatChannelTitle = messages.StringField(4)
    post_count = messages.IntegerField(5, variant=messages.Variant.INT32)

    channel_type = messages.StringField(7)

    chatChannelKeyIdStr = messages.StringField(20)
    chatChannelKeyId = messages.IntegerField(21, variant=messages.Variant.INT32)

    chatChannelRefKeyIdStr = messages.StringField(22)
    chatChannelRefKeyId = messages.IntegerField(23, variant=messages.Variant.INT32)

    chatChannelOwnerKeyIdStr = messages.StringField(24)
    chatChannelOwnerKeyId = messages.IntegerField(25, variant=messages.Variant.INT32)

    online = messages.BooleanField(50)

    response_message = messages.StringField(140)
    response_successful = messages.BooleanField(150)


class ChatChannelSubscriberCreateRequest(messages.Message):
    """ create a ChatSubscriber - Coming in over the API, this is just text """
    chatChannelKey = messages.StringField(1)


CHAT_CHANNEL_SUBSCRIBER_CREATE_RESOURCE = endpoints.ResourceContainer(
    ChatChannelSubscriberCreateRequest
)

class ChatChannelSubscriberCollection(messages.Message):
    """ multiple chat Subscribers """
    chat_channel_subscribers = messages.MessageField(ChatChanelSubscriberGetResponse, 1, repeated=True)
    response_message = messages.StringField(140)
    response_successful = messages.BooleanField(150)
