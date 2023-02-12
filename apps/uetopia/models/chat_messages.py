import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class ChatMessages(ndb.Model):
    """ a message that goes out over a chat channel.
    can contain data and/or text

    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    chatChannelKeyId = ndb.IntegerProperty()
    chatChannelTitle = ndb.StringProperty()

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty()

    command = ndb.StringProperty()
    option = ndb.StringProperty()
    target = ndb.StringProperty()
    target_type = ndb.StringProperty()

    text = ndb.StringProperty()
    data_string = ndb.StringProperty()

    #pulled = ndb.BooleanProperty()

    def to_json(self):
        return ({
                u'key': self.key.urlsafe(),
                u'chatChannelKeyId': self.chatChannelKeyId,
                u'chatChannelTitle': self.chatChannelTitle,
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                u'command': self.command,
                u'option': self.option,
                u'target': self.target,
                u'target_type': self.target_type,
                u'text': self.text,
                u'data_string': self.data_string
        })

class ChatMessageGetResponse(messages.Message):
    """ a ChatMessage's data """
    key = messages.StringField(1)
    command = messages.StringField(2)
    option = messages.StringField(3)
    target = messages.StringField(4)
    target_type = messages.StringField(5)
    text = messages.StringField(6)
    data_string = messages.StringField(7)
    response_message = messages.StringField(140)
    response_successful = messages.BooleanField(150)

class ChatMessageCreateRequest(messages.Message):
    """ create a ChatMessage - Coming in over the API, this is just text """
    chatChannelKeyId = messages.StringField(1)
    text = messages.StringField(2)
    channel_id = messages.StringField(3)
    userKeyId = messages.StringField(4)


CHAT_MESSAGE_CREATE_RESOURCE = endpoints.ResourceContainer(
    ChatMessageCreateRequest
)
