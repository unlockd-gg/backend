import logging
import hashlib
import hmac
import urllib
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.match_players import MatchPlayers
from configuration import *

class MatchPlayersController(BaseController):
    """MatchPlayer Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = MatchPlayers

    def get_list_by_matchKeyId(self, matchKeyId):
        """ get all for a match """

        query = self.model.query()
        query = query.filter(self.model.matchKeyId == matchKeyId)
        query = query.order(self.model.created)
        return query.fetch(1000)

    def list_page_pending_by_gameKeyId_descending(self, gameKeyId, page_size=1000, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.matchmakerPending == True)
        query = query.order(-self.model.created)
        results, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return results, cursor, more

    def list_page_pending_by_matchTaskStatusKeyId_descending(self, matchTaskStatusKeyId, page_size=1000, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.matchTaskStatusKeyId == matchTaskStatusKeyId)
        query = query.filter(self.model.matchmakerPending == True)
        query = query.order(-self.model.created)
        results, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return results, cursor, more

    def list_pending_stale(self):
        query = self.model.query()
        query = query.filter(self.model.stale < datetime.datetime.now())
        query = query.filter(self.model.stale_requires_check == True)
        return query.fetch(1000)

    def get_list_by_userKeyId(self, userKeyId):
        """ get all for a player """

        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.order(-self.model.created)
        return query.fetch(1000)

    def get_by_matchKeyId_userKeyId(self, matchKeyId, userKeyId):
        """ get a single match player by matchkey and playerkey """

        query = self.model.query()
        query = query.filter(self.model.matchKeyId == matchKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_pending_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get a single match player by matchkey and playerkey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.matchmakerPending == True)
        return query.get()

    def get_joinable_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get a single match player by matchkey and playerkey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.matchmakerJoinable == True)
        return query.get()

    def get_join_pending_by_gameKeyId_userKeyId(self, gameKeyId, userKeyId):
        """ get a single match player by matchkey and playerkey """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.matchmakerJoinPending == True)
        return query.get()

    def get_join_pending_by_userKeyId(self, userKeyId):
        """ get a single match player by user key """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.matchmakerJoinPending == True)
        return query.get()

    def get_recent_by_userKeyId(self, userKeyId):
        """ get recent for a player """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.order(-self.model.created)
        return query.fetch(3)

    def get_opponents_by_matchKeyId_userKeyId(self, matchKeyId, userKeyId):
        """ get recent for a player """
        query = self.model.query()
        query = query.filter(self.model.matchKeyId == matchKeyId)
        query = query.filter(self.model.userKeyId != userKeyId)
        return query.fetch(30)

    def list_joinable_stale(self):
        query = self.model.query()
        startdate = datetime.datetime.now()
        staledate = startdate - MATCH_PLAYER_AUTO_EXPIRE_TIME
        query = query.filter(self.model.modified < staledate)
        query = query.filter(self.model.matchmakerJoinable == True)
        query = query.filter(self.model.stale_requires_check == True)
        return query.fetch(1000)

    def list_joinPending_stale(self):
        query = self.model.query()
        startdate = datetime.datetime.now()
        staledate = startdate - MATCH_PLAYER_AUTO_EXPIRE_TIME
        query = query.filter(self.model.modified < staledate)
        query = query.filter(self.model.matchmakerJoinPending == True)
        query = query.filter(self.model.stale_requires_check == True)
        return query.fetch(1000)

    def list_pending_by_userKeyId(self, userKeyId):
        """ list match players by playerkey """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.matchmakerPending == True)
        return query.fetch(1000)
