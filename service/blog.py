import endpoints
import logging
import uuid
import urllib
import json
import dateutil.parser
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from slugify import slugify

##from apps.uetopia.providers import firebase_helper

## endpoints v2 wants a "collection" so it can build the openapi files
#from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.models.posts import *

from apps.uetopia.controllers.posts import PostsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']


@endpoints.api(name="blog", version="v1", description="Blog API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class BlogApi(remote.Service):
    @endpoints.method(POST_RESOURCE, PostResponse, path='postCreate', http_method='POST', name='post.create')
    ##@Games.method(path="games", http_method="POST", name="games.create")
    def postCreate(self, request):
        """ Create a post - PROTECTED - ADMIN ONLY """
        logging.info("postCreate")
        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return PostResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #claims = firebase_helper.verify_auth_token(self.request_state)
        if not claims:
            logging.error('Firebase Unauth')
            return PostResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return PostResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('not admin')
            return PostResponse(response_message='Error: Only users with admin permissions may create posts. ', response_successful=False)

        ## ONLY allow this from authorized domains
        #request_origin = self.request_state.headers['origin']
        #logging.info("request_origin: %s" %request_origin)
        #if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
        #    logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
        #    return PostResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)


        postController = PostsController()

        ## slugify the title
        title_slugify = slugify(request.title)

        post = postController.create(
            slugify_url = title_slugify,
            title = request.title,
            banner_url = request.banner_url,
            summary = request.summary,
            body =request.body,
            tags = request.tags or [],
            author_name = authorized_user.title,
            author_userKeyId = authorized_user.key.id()
            )


        return PostResponse(response_message="Post Created", response_successful=True)


    @endpoints.method(POST_COLLECTION_PAGE_RESOURCE, PostCollection, path='postCollectionGetPage', http_method='POST', name='post.collection.get.page')
    def postCollectionGetPage(self, request):
        """ Get a collection of posts """
        logging.info("postCollectionGetPage")

        # No auth required

        postController = PostsController()

        if request.cursor:
            curs = Cursor(urlsafe=request.cursor)
        else:
            curs = Cursor()

        #sort_order = request.sort_order
        #direction = request.direction

        posts = []

        posts, cursor, more = postController.list_page_reverse_chrono(start_cursor=curs)

        entity_list = []
        for post in posts:
            entity_list.append(PostResponse(
                key_id = post.key.id(),
                #created= post.created.isoformat(' '),
                created = post.created.strftime('%Y-%m-%d'),
                slugify_url = post.slugify_url,
                banner_url = post.banner_url,
                title = post.title,
                summary = post.summary,
                tags = post.tags,
                author_name = post.author_name,
                author_userKeyId = str(post.author_userKeyId)
            ))

        #if cursor:
        #    cursor_urlsafe = cursor.urlsafe()
        #else:
        #    cursor_urlsafe = None

        response = PostCollection(
            posts = entity_list,
            #more = more,
            #cursor = cursor_urlsafe,
        )

        return response

    @endpoints.method(POST_RESOURCE, PostResponse, path='postGet', http_method='POST', name='get')
    def postGet(self, request):
        """ Get a post """
        logging.info("postGet")

        # No auth required

        postController = PostsController()

        ## Get the post by slugify_url
        post = postController.get_by_slugify_url(request.slugify_url)
        if not post:
            logging.info('no post record found')
            return VoucherResponse(response_message='Error: No post Record Found. ', response_successful=False)


        ## also get the author photo and description
        author = UsersController().get_by_key_id(post.author_userKeyId)

        return PostResponse(
            key_id = post.key.id(),
            created= post.created.strftime('%Y-%m-%d'),
            slugify_url = post.slugify_url,
            banner_url = post.banner_url,
            title = post.title,
            body = post.body,
            tags = post.tags,
            author_name = post.author_name,
            author_userKeyId = str(post.author_userKeyId),
            author_picture = author.picture,
            author_bio = author.description
        )
