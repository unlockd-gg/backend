import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.games import Games

class GamesController(BaseController):
    """Games Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Games

    def get_by_userKeyId(self, userKeyId):
        """ get list by developer key """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)


    def get_supported_games(self):
        """ get supported games """
        query = self.model.query()
        query = query.filter(self.model.supported == True)
        query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.approved == True)
        return query.fetch(1000)

    def get_supported_games_ordered(self):
        """ get supported games """
        query = self.model.query()
        query = query.filter(self.model.supported == True)
        query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.approved == True)
        query = query.order(self.model.order)
        return query.fetch(1000)

    def get_all_public(self):
        """ get all openToAllDevelopers """
        query = self.model.query()
        query = query.filter(self.model.openToAllDevelopers == True)
        return query.fetch(1000)

    def get_visible(self):
        """ get games """
        query = self.model.query()
        query = query.filter(self.model.invisible == False)
        return query.fetch(1000)

    def get_visible_dev(self):
        """ get visible-dev games  """
        query = self.model.query()
        query = query.filter(self.model.invisible_developer_setting == False)
        return query.fetch(1000)
