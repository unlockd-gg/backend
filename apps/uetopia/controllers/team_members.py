import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.team_members import TeamMembers

class TeamMembersController(BaseController):
    """TeamMembers Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = TeamMembers

    def get_by_teamKeyId(self, teamKeyId):
        """ get all team members """
        query = self.model.query()
        query = query.filter(self.model.teamKeyId == teamKeyId)
        return query.fetch(1000)

    def get_by_teamKeyId_userKeyId(self, teamKeyId, userKeyId):
        """ get all team members """
        query = self.model.query()
        query = query.filter(self.model.teamKeyId == teamKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_by_nextTournamentKeyId_userKeyId(self, nextTournamentKeyId, userKeyId):
        """ get all team members """
        query = self.model.query()
        query = query.filter(self.model.nextTournamentKeyId == nextTournamentKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def list_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get all team members """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(100)

    def get_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get single team members """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_invited_by_invitedByUserKeyId_userKeyId(self,invitedByUserKeyId,userKeyId):
        """ get a team player invitation """
        query = self.model.query()
        query = query.filter(self.model.invitedByUserKeyId == invitedByUserKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.invited == True)
        return query.get()
