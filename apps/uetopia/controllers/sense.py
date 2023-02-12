from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.sense import Sense

class SenseController(BaseController):
    """Sense Controller"""
    def __init__(self):
        
        self._default_order = 'created'
        self.model = Sense
        
    def get_recent_by_userKey(self, target_key):
        """ get recent for a user """
        query = self.model.query()
        query = query.filter(self.model.target_key == target_key)
        query = query.order(-self.model.created)
        return query.fetch(100)