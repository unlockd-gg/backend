import logging
import hashlib
import hmac
import urllib
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.match_task_status import MatchTaskStatus
from configuration import *

class MatchTaskStatusController(BaseController):
    """MatchTaskStatus Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = MatchTaskStatus

    def get_list_by_region_mode_rankMin(self, region, mode, rankMin):
        query = self.model.query()
        query = query.filter(self.model.region == region)
        query = query.filter(self.model.mode == mode)
        query = query.filter(self.model.rankMin <= rankMin)
        return query.fetch(1000)

    def get_list_by_game_algorithm_region_mode_rankMin(self, gameKeyId, matchmakerAlgorithm, region, mode, rankMin):
        if region:
            query = self.model.query()
            query = query.filter(self.model.gameKeyId == gameKeyId)
            query = query.filter(self.model.matchmakerAlgorithm == matchmakerAlgorithm)
            query = query.filter(self.model.region == region)
            query = query.filter(self.model.mode == mode)
            query = query.filter(self.model.rankMin <= rankMin)
            return query.fetch(1000)
        else:
            query = self.model.query()
            query = query.filter(self.model.gameKeyId == gameKeyId)
            query = query.filter(self.model.matchmakerAlgorithm == matchmakerAlgorithm)
            query = query.filter(self.model.mode == mode)
            query = query.filter(self.model.rankMin <= rankMin)
            return query.fetch(1000)
