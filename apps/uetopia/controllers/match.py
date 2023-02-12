import logging
import hashlib
import hmac
import urllib
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.match import Match
from configuration import *

class MatchController(BaseController):
    """Match Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Match

    def get_public_open_list(self):
        query = self.model.query()
        query = query.filter(self.model.allPlayersJoined == False)
        query = query.filter(self.model.public == True)
        return query.fetch(1000)

    def get_games_public_open_list(self, gameKeyId):
        query = self.model.query()
        query = query.filter(self.model.allPlayersJoined == False)
        query = query.filter(self.model.public == True)
        query = query.filter(self.model.matchExpired == False)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.order(-self.model.created)
        return query.fetch(1000)

    def get_games_public_open_list_with_region(self, gameKeyId, region):
        query = self.model.query()
        query = query.filter(self.model.allPlayersJoined == False)
        query = query.filter(self.model.public == True)
        query = query.filter(self.model.matchExpired == False)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.region == region)
        query = query.order(-self.model.created)
        return query.fetch(1000)


    def get_matches_not_all_verified_expired(self):
        previous_date = datetime.datetime.now() - MATCHMAKER_MAXIMUM_HOST_VERIFICATION_GRACE_PERIOD
        query = self.model.query()
        query = query.filter(self.model.allPlayersVerified == False)
        query = query.filter(self.model.matchExpired == False)
        query = query.filter(self.model.created < previous_date)
        return query.fetch(1000)

    def get_matches_not_all_verified_expired_invalid(self):
        previous_date = datetime.datetime.now() - MATCHMAKER_MAXIMUM_HOST_VERIFICATION_GRACE_PERIOD
        query = self.model.query()
        query = query.filter(self.model.allPlayersVerified == False)
        query = query.filter(self.model.matchExpired == False)
        query = query.filter(self.model.matchVerifyBeforePurge == False)
        query = query.filter(self.model.created < previous_date)
        return query.fetch(1000)

    def get_group_visible_list(self, groupKeyId):
        query = self.model.query()
        query = query.filter(self.model.allPlayersJoined == False)
        query = query.filter(self.model.public == True)
        query = query.filter(self.model.matchExpired == False)
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.order(-self.model.created)
        return query.fetch(1000)

    def get_games_public_feed(self, gameKeyId):
        query = self.model.query()
        query = query.filter(self.model.public == True)
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.order(-self.model.created)
        return query.fetch(100)

    def get_matches_public_not_all_committed_not_expired(self):
        #previous_date = datetime.datetime.now() - MATCHMAKER_MATCH_TIMEOUT_NOT_COMMITTED
        query = self.model.query()
        query = query.filter(self.model.allPlayersCommitted == False)
        query = query.filter(self.model.matchExpired == False)
        query = query.filter(self.model.public == True)

        #query = query.filter(self.model.created > previous_date)
        return query.fetch(1000)

    def get_matches_by_tournamentKeyId(self, tournamentKeyId):
        query = self.model.query()
        query = query.filter(self.model.tournamentKeyId == tournamentKeyId)
        return query.fetch(1000)

    def get_matches_by_tournamentKeyId_tournamentTier(self, tournamentKeyId, tournamentTier):
        query = self.model.query()
        query = query.filter(self.model.tournamentKeyId == tournamentKeyId)
        query = query.filter(self.model.tournamentTier == tournamentTier)
        return query.fetch(1000)

    def get_list_by_game(self, gameKeyId):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)
