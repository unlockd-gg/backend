import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.tournament_sponsors import TournamentSponsors
from configuration import *

class TournamentSponsorsController(BaseController):
    """Tournament Sponsors Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = TournamentSponsors

    def get_list_by_tournamentKeyId(self, tournamentKeyId):
        #previous_date = datetime.datetime.now() - MATCHMAKER_MATCH_TIMEOUT_NOT_COMMITTED
        query = self.model.query()
        query = query.filter(self.model.tournamentKeyId == tournamentKeyId)
        return query.fetch(1000)

    def get_by_tournamentKeyId_groupKeyId(self, tournamentKeyId, groupKeyId):
        #previous_date = datetime.datetime.now() - MATCHMAKER_MATCH_TIMEOUT_NOT_COMMITTED
        query = self.model.query()
        query = query.filter(self.model.tournamentKeyId == tournamentKeyId)
        query = query.filter(self.model.groupKeyId == groupKeyId)
        return query.get()
