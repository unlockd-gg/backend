import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.tournaments import Tournaments
from configuration import *

class TournamentsController(BaseController):
    """Tournament Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Tournaments

    def get_public_not_completed(self):
        #previous_date = datetime.datetime.now() - MATCHMAKER_MATCH_TIMEOUT_NOT_COMMITTED
        query = self.model.query()
        query = query.filter(self.model.groupMembersOnly == False)
        query = query.filter(self.model.completed == False)
        return query.fetch(1000)

    def get_stale_not_completed(self):
        ## Get old tournaments that never finished
        previous_date = datetime.datetime.now() - TOURNAMENT_TIMEOUT_NOT_COMPLETED
        query = self.model.query()
        query = query.filter(self.model.completed == False)
        query = query.filter(self.model.modified < previous_date)
        return query.fetch(1000)

    def get_public_not_completed_by_gameKeyId(self, gameKeyId):
        #previous_date = datetime.datetime.now() - MATCHMAKER_MATCH_TIMEOUT_NOT_COMMITTED
        query = self.model.query()
        query = query.filter(self.model.groupMembersOnly == False)
        query = query.filter(self.model.completed == False)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def get_group_not_completed_by_gameKeyId(self, gameKeyId, groupKeyId):
        #previous_date = datetime.datetime.now() - MATCHMAKER_MATCH_TIMEOUT_NOT_COMMITTED
        query = self.model.query()
        query = query.filter(self.model.groupMembersOnly == True)
        query = query.filter(self.model.completed == False)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.groupKeyId == groupKeyId)
        return query.fetch(1000)
