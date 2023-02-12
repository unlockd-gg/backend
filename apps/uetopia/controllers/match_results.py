import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.match_results import MatchResults

class MatchResultsController(BaseController):
    """Game Controller"""
    def __init__(self):
        
        self._default_order = 'created'
        self.model = MatchResults
        
    def get_recent_for_server(self, serverKey, count=6):
        """ get recent match results for a server """
        query = self.model.query()
        query = query.filter(self.model.serverKey == serverKey)
        query = query.order(-self.model.created)
        return query.fetch(count)

    def list_page_filtered(self, page_size=20, batch_size=5, start_cursor=None, order=None, filter_by=None, filter_key=None):
        query = self.model.query()
        
        if filter_by == "gameKey":
            query = query.filter(self.model.gameKey == filter_key)
            logging.info("filtering by gameKey")
        elif filter_by == "serverKey":
            query = query.filter(self.model.serverKey == filter_key)
            logging.info("filtering by serverKey")
        elif filter_by == "userKey":
            query = query.filter(self.model.userList.IN([filter_key]))
            logging.info("filtering by userList")
        
        if order == 'created':
            query_forward = query.order(self.model.created)
            #query_backward = query.order(-order)
        else:
            query_forward = query.order(-self.model.created)
            #query_backward = query.order(-self.model.key)
            
        ecodes, cursor, more = query_forward.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        
        # Fetch the same page going backward.
        #rev_cursor = start_cursor.reversed()
        #bars1, cursor_back, less = query_backward.fetch_page(page_size, start_cursor=rev_cursor, batch_size=batch_size)
        
        return ecodes, cursor, more#, cursor_back, less
    