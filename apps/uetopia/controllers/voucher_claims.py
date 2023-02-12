import logging
import datetime
from google.appengine.api import memcache
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.voucher_claims import VoucherClaims

class VoucherClaimsController(BaseController):
    """Voucher Claims Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = VoucherClaims

    def get_all_sorted_by_voucherKeyId(self, voucherKeyId):
        """ get all for a voucherKeyId """
        query = self.model.query()
        query = query.filter(self.model.voucherKeyId == voucherKeyId)
        query = query.order(self.model.created)
        return query.fetch(1000)
