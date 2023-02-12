import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class Posts(ndb.Model):
    """ Posts are articles for the blog """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    slugify_url = ndb.StringProperty(indexed=True)
    title = ndb.StringProperty(indexed=False)
    banner_url = ndb.StringProperty(indexed=False)
    summary = ndb.TextProperty(indexed=False)
    body = ndb.TextProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True, indexed=False)
    author_name = ndb.StringProperty(indexed=False)
    author_userKeyId = ndb.IntegerProperty(indexed=False)



class PostResponse(messages.Message):
    """ an post's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    created = messages.StringField(100) # DATETIME
    slugify_url = messages.StringField(101)
    title = messages.StringField(102)
    author_name = messages.StringField(103)
    author_userKeyId = messages.StringField(104)
    author_picture = messages.StringField(105)
    author_bio = messages.StringField(106)

    body = messages.StringField(2)
    banner_url = messages.StringField(3)
    summary = messages.StringField(4)
    tags = messages.StringField(7, repeated=True)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class PostRequest(messages.Message):
    """ an post's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32) ## key is forbidden incoming
    title = messages.StringField(2)
    body = messages.StringField(3)
    banner_url = messages.StringField(4)
    summary = messages.StringField(5)
    slugify_url = messages.StringField(6)

    tags = messages.StringField(7, repeated=True)

POST_RESOURCE = endpoints.ResourceContainer(
    PostRequest
)

class PostCollection(messages.Message):
    """ multiple posts """
    posts = messages.MessageField(PostResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class PostCollectionPageRequest(messages.Message):
    """ a post collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

POST_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    PostCollectionPageRequest
)
