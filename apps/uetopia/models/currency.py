import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class Currency(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    title = ndb.StringProperty()
    iso_code = ndb.StringProperty()
    value_to_usd = ndb.FloatProperty()

    def to_json(self):
        one_hundred_million_cred_equals = 1.0 / self.value_to_usd #9256.19460179101
        one_cred_equals = '%f' % (one_hundred_million_cred_equals/100000000.)  #'0.000093'
        one_cred_equals_float = float(one_cred_equals) # 0.000093
        return ({
            u'value_to_usd': one_cred_equals_float
            })
