import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.teams import Teams

class TeamsController(BaseController):
    """Team Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Teams

    def get_by_tournament_captain(self, nextTournamentKeyId, captainPlayerKeyId):
        """ get a team for a tournament by playerkey """
        query = self.model.query()
        query = query.filter(self.model.nextTournamentKeyId == nextTournamentKeyId)
        query = query.filter(self.model.captainPlayerKeyId == captainPlayerKeyId)
        return query.get()

    def get_list_by_tournament(self, nextTournamentKeyId):
        """ get all teams for a tournament """
        query = self.model.query()
        query = query.filter(self.model.nextTournamentKeyId == nextTournamentKeyId)
        return query.fetch(1000)

    def get_list_by_tournament_full(self, nextTournamentKeyId):
        """ get all FULL teams for a tournament """
        query = self.model.query()
        query = query.filter(self.model.nextTournamentKeyId == nextTournamentKeyId)
        query = query.filter(self.model.teamFull == True)
        return query.fetch(1000)

    def get_list_by_tournament_not_eliminated(self, nextTournamentKeyId):
        """ get all remaining teams for a tournament """
        query = self.model.query()
        query = query.filter(self.model.nextTournamentKeyId == nextTournamentKeyId)
        query = query.filter(self.model.nextTournamentEliminated == False)
        return query.fetch(1000)
