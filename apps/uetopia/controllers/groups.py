import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.groups import Groups

class GroupsController(BaseController):
    """Groups Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Groups

    def get_by_ownerPlayerKeyId(self, ownerPlayerKeyId):
        """ get group owend by a player """
        query = self.model.query()
        query = query.filter(self.model.ownerPlayerKeyId == ownerPlayerKeyId)
        return query.get()

    def get_by_tag(self, tag):
        """ get group by tag """
        query = self.model.query()
        query = query.filter(self.model.tag == tag)
        return query.get()

    def list_visible_page(self, page_size=100, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.invisible == False)
        items, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return items, cursor, more
