import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.developer import Developer

class DeveloperController(BaseController):
    """Develop Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Developer

    def get_by_userKey(self, userKey):
        """ get a developer for a user """
        query = self.model.query()
        query = query.filter(self.model.userKey == userKey)
        return query.get()
