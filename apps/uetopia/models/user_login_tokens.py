from google.appengine.ext import ndb


class UserLoginTokens(ndb.Model):
    """ a place to store login tokens that is isolated from a users account.
    This may change and get updated irregulary, and we don't want it to overlap with a different user update process.

    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    userKeyId = ndb.IntegerProperty()
    access_token = ndb.StringProperty()
    
