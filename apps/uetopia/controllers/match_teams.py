import logging
import hashlib
import hmac
import urllib
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.match_teams import MatchTeams
from configuration import *

class MatchTeamsController(BaseController):
    """MatchTeam Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = MatchTeams
