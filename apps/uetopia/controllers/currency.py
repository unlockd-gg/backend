import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.currency import Currency

class CurrencyController(BaseController):
    """Currency Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Currency

    def get_by_iso_code(self, iso_code):
        """ get all for a iso_code there should only be one. """

        query = self.model.query()
        query = query.filter(self.model.iso_code == iso_code)
        return query.get()
