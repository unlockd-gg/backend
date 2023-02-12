import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.match_results_user import MatchResultsUser

class MatchResultsUserController(BaseController):
    """Game Controller"""
    def __init__(self):
        
        self._default_order = 'created'
        self.model = MatchResultsUser
        
    def get_list_by_userKey(self, userKey):
        """ get all for a match results user """

        query = self.model.query()
        query = query.filter(self.model.userKey == userKey)
        query = query.order(-self.model.created)
        return query.fetch(1000)