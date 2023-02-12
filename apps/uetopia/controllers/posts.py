import logging
import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.posts import Posts

class PostsController(BaseController):
    """Posts Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Posts

    def list_page_reverse_chrono(self, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query_forward = query.order(-self.model.created)
        posts, cursor, more = query_forward.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return posts, cursor, more

    def get_by_slugify_url(self, slugify_url):
        query = self.model.query()
        query = query.filter(self.model.slugify_url == slugify_url)
        return query.get()
