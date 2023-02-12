import logging
import json
import uuid
from google.appengine.api import taskqueue
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.transactions import Transactions

class TransactionsController(BaseController):
    """Transaction Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Transactions

    def get_recent_by_userKeyId(self, userKeyId):
        """ get the latest transactions by player key """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.order(-self.model.created)
        return query.fetch(100)

    def get_by_transaction_hash(self, t_hash):
        """ get the transaction by the hash/xapo id """
        query = self.model.query()
        query = query.filter(self.model.transaction_hash == t_hash)
        return query.get()

    def get_all_by_userKeyId(self, userKeyId):
        """ get the latest transactions by player key """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)

    def get_pending_by_serverKeyId(self, serverKeyId):
        """ get the latest transactions by player key """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.transactionType == "server")
        query = query.filter(self.model.processed == False)
        return query.fetch(1000)

    def get_pending_by_vendorKeyId(self, vendorKeyId):
        """ get the latest transactions by player key """
        query = self.model.query()
        query = query.filter(self.model.vendorKeyId == vendorKeyId)
        query = query.filter(self.model.transactionType == "vendor")
        query = query.filter(self.model.processed == False)
        return query.fetch(1000)

    def get_pending_by_userKeyId(self, userKeyId):
        """ get the latest transactions by player key """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.transactionType == "user")
        query = query.filter(self.model.processed == False)
        return query.fetch(1000)

    def get_pending_by_gameKeyId(self, gameKeyId):
        """ get the latest transactions by game key """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.transactionType == "game")
        query = query.filter(self.model.processed == False)
        query = query.order(self.model.created)
        return query.fetch(1000)

    def get_pending_by_groupKeyId(self, groupKeyId):
        """ get the latest transactions by group key """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.transactionType == "group")
        query = query.filter(self.model.processed == False)
        return query.fetch(1000)

    def get_pending_by_adKeyId(self, adKeyId):
        """ get the latest transactions by group key """
        query = self.model.query()
        query = query.filter(self.model.adKeyId == adKeyId)
        query = query.filter(self.model.transactionType == "ad")
        query = query.filter(self.model.processed == False)
        return query.fetch(1000)


    def get_pending_by_serverPlayerKeyId(self, serverPlayerKeyId):
        """ get the latest transactions by player key """
        query = self.model.query()
        query = query.filter(self.model.serverPlayerKeyId == serverPlayerKeyId)
        query = query.filter(self.model.transactionType == "serverplayer")
        query = query.filter(self.model.processed == False)
        return query.fetch(1000)

    def list_page_by_serverKeyId(self, serverKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.transactionType == 'server')
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_by_gameKeyId(self, gameKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.transactionType == 'game')
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_by_userKeyId(self, userKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.transactionType == 'user')
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_by_serverPlayerKeyId(self, serverPlayerKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.serverPlayerKeyId == serverPlayerKeyId)
        query = query.filter(self.model.transactionType == 'serverplayer')
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_by_groupKeyId(self, groupKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.transactionType == 'group')
        query = query.order(-self.model.created)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more
