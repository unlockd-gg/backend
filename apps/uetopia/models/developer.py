import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

### DEPRECATED - UNUSED - TODO delete

class Developer(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    googleUser = ndb.StringProperty(indexed=False)

    userKey = ndb.StringProperty() # connect to a user account?

    title = ndb.StringProperty(indexed=False)
    invisible = ndb.BooleanProperty(indexed=False)
    applied = ndb.BooleanProperty(indexed=False)
    application_date = ndb.DateTimeProperty(indexed=False)
    approved = ndb.BooleanProperty(indexed=False)
    approval_date = ndb.DateTimeProperty(indexed=False)
    approved_by = ndb.StringProperty(indexed=False)

    answer1 = ndb.TextProperty(indexed=False)
    answer2 = ndb.TextProperty(indexed=False)
    answer3 = ndb.TextProperty(indexed=False)

    ## Api stuff
    apiKey = ndb.StringProperty()
    apiSecret = ndb.StringProperty(indexed=False)

### PROTORPC MODELS FOR ENDPOINTS

class DeveloperGetResponse(messages.Message):
    """ a developer's data """
    developerKey = messages.StringField(1)
    invisible = messages.BooleanField(2)
    approved = messages.BooleanField(3)
    apiKey = messages.StringField(4)
    apiSecret = messages.StringField(5)
    message = messages.StringField(6)


class DeveloperCreateRequest(messages.Message):
    """ create a developer """
    title = messages.StringField(1)
    answer1 = messages.StringField(2)
    answer2 = messages.StringField(3)
    answer3 = messages.StringField(4)


DEVELOPER_CREATE_RESOURCE = endpoints.ResourceContainer(
    DeveloperCreateRequest
)
