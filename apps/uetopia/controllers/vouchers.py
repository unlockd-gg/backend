import logging
import datetime
from google.appengine.api import memcache
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.vouchers import Vouchers

from configuration import *

class VouchersController(BaseController):
    """Vouchers Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Vouchers

    def get_by_offerKeyId(self, offerKeyId):
        """ get all for a offerKeyId """
        query = self.model.query()
        query = query.filter(self.model.offerKeyId == offerKeyId)
        return query.fetch(1000)

    def get_by_gameKeyId(self, gameKeyId):
        """ get all for a offerKeyId """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def memcache_get(self, memcacheKey):
        """ get memcached data """
        data = memcache.get(memcacheKey)
        return data

    def memcache_set(self, memcacheKey):
        """ set the latest time """
        memcache.set(memcacheKey, datetime.datetime.now())
        return

    def redeemable(self, memcacheKey, seconds=None):
        """ True if the channel has not had a push recently """
        data = self.memcache_get(memcacheKey)
        if data is not None:
            now = datetime.datetime.now()
            if seconds:
                seconds_t = datetime.timedelta(seconds=seconds)
                earlier = now - seconds_t
            else:
                earlier = now - SERVER_TRANSACTION_QUEUE_MINIMUM_INTERVAL
            if data > earlier:
                return False
            else:
                self.memcache_set(memcacheKey)
                return True
        else:
            self.memcache_set(memcacheKey)
            return True
