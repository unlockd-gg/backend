import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.orders import Orders

class OrdersController(BaseController):
    """Orders Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Orders
