import endpoints
import logging
import uuid
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
import PyRSS2Gen

from apps.handlers import BaseHandler
from apps.uetopia.controllers.posts import PostsController

from configuration import *

class FeedHandler(BaseHandler):
    def get(self):
        logging.info("FeedHandler")

        start = datetime.datetime.now() - datetime.timedelta(days=60)
        count = (int(self.request.get('count'
                 )) if not self.request.get('count') == '' else 1000)

        postController = PostsController()

        curs = Cursor()
        posts, cursor, more = postController.list_page_reverse_chrono(start_cursor=curs)

        #servers = ServerController().get_visible_by_game_key(game.key.urlsafe())

        feed_title = "UETOPIA"
        lastBuildDate = datetime.datetime.utcnow(),

        entities = []

        lastBuildDate = datetime.datetime.now()
        updated = ""
        game_title = ""

        if posts is not None and len(posts) > 0:
            updated = posts[0].modified.strftime('%Y-%m-%dT%H:%M:%S')
            lastBuildDate = posts[0].modified

        items = [PyRSS2Gen.RSSItem(
            title = x.title,
            link = "http://uetopia.com/#/blog/" + x.slugify_url,
            description = x.body,
            guid = PyRSS2Gen.Guid("http://uetopia.com/#/blog/" + x.slugify_url),
            pubDate = x.created.strftime("%a, %d %b %Y %H:%M:%S GMT"))
            for x in posts]

        # make the RSS2 object
        rss = PyRSS2Gen.RSS2(
            title = feed_title,
            link = "https://uetopia.com",
            image = PyRSS2Gen.Image("https://uetopia.com/img/logo_square.png", "Logo", "https://uetopia.com/"),
            #image = "https://uetopia.com/img/logo_square.png",
            description = feed_title,
            lastBuildDate = lastBuildDate,
            ttl = 1,
            items = items)

        #emit the feed
        xml = rss.to_xml()

        #template_values = {'entities': entities,
        #                    'updated': updated,
        #                    'game_title': game_title,
        #                    'request': self.request,
        #                   'host': os.environ.get('HTTP_HOST',
        #                   os.environ['SERVER_NAME'])}


        return self.render_xml_rss_response(
            xml
        )
