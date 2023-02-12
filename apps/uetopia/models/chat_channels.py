import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class ChatChannels(ndb.Model):
    """ a chat channel.


    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    refKeyId = ndb.IntegerProperty(indexed=True)

    ## we also want a dedicated gameKeyId for all chat channels that are not custom
    gameKeyId = ndb.IntegerProperty(indexed=False)

    title = ndb.StringProperty(indexed=True)
    description = ndb.TextProperty(indexed=False)

    #text_enabled = ndb.BooleanProperty()
    #data_enabled = ndb.BooleanProperty()

    channel_type = ndb.StringProperty(indexed=True)  # game, player, group, server,

    adminUserKeyId = ndb.IntegerProperty(indexed=True)
    adminUserTitle = ndb.StringProperty(indexed=False)

    max_subscribers = ndb.IntegerProperty(indexed=False)

    region = ndb.StringProperty(indexed=True)


    ## discord integration


class ChatChanelGetResponse(messages.Message):
    """ a ChatChannel's data """
    key_id = messages.IntegerField(1)
    refKeyId = messages.StringField(2)
    title = messages.StringField(3)
    description = messages.StringField(4)
    #text_enabled = messages.BooleanField(5)
    #data_enabled = messages.BooleanField(6)
    adminUserKeyId = messages.StringField(7)
    adminUserTitle = messages.StringField(8)
    max_subscribers = messages.IntegerField(9)
    response_message = messages.StringField(140)
    response_successful = messages.BooleanField(150)

class ChatChannelCreateRequest(messages.Message):
    """ create a ChatChannel - Coming in over the API, this is just text """
    title = messages.StringField(1)
    description = messages.StringField(2)


CHAT_CHANNEL_CREATE_RESOURCE = endpoints.ResourceContainer(
    ChatChannelCreateRequest
)

class ChatChannelCollection(messages.Message):
    """ multiple chat channels """
    chat_channels = messages.MessageField(ChatChanelGetResponse, 1, repeated=True)
    response_message = messages.StringField(140)
    response_successful = messages.BooleanField(150)

class ChatChannelConnectRequest(messages.Message):
    """ connect a ChatChannel - Coming in over the API, this is just text """
    key_id = messages.StringField(1)
    title = messages.StringField(2)

CHAT_CHANNEL_CONNECT_RESOURCE = endpoints.ResourceContainer(
    ChatChannelConnectRequest
)
