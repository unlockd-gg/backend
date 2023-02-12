from datetime import datetime
import time
from uuid import uuid4
import logging
import functools
from google.appengine.api import users
import webapp2
import json
from webapp2_extras import jinja2, sessions


class BaseHandler(webapp2.RequestHandler):

    __UUID_SESSION_KEY = "user_uuid"

    def _dispatch_hook(self):
        """Subclasses override this to implement custom pre-dispatch behaviour,
        after BaseHandler.dispatch but before calling webapp2.RequestHandlers
        dispatch method"""

        # Used by UserHandler to ensure user is authenticated with correct
        # credentials before allowing them to proceed
        pass


    @property
    def user_uuid(self):
        """Returns a UUID for the user from their session. Can be used to track user
        activity when login isn't required."""
        return self.session.get(self.__UUID_SESSION_KEY)


    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


    @property
    def is_sdk(self):
        """Indicates that we're running on the local development app server"""
        return common.IS_SDK


    @property
    def is_remote_dev(self):
        """Indicates that we're running on a development version on appspot.com"""
        return common.IS_REMOTE_DEV

    @property
    def requested_response_format(self):
        """The requested format of the response, per the query string. Defaults
        to 'html' if no value was supplied. Use to specify JSON or other response
        formats."""
        return self.request.get("format", "html")

    def format_currency(self, value):
        return "${:,.2f}".format(value)

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        jinja2_obj = jinja2.get_jinja2(app=self.app)

        jinja2_obj.environment.filters['format_currency'] = self.format_currency

        return jinja2_obj


    def render_html_response(self, template, http_code=200, **context):
        """Renders a Jinja2 template with the given context"""


        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)
        self.response.status = http_code


    def render_json_response(self, http_code=200, **kwargs):
        """Renders kwargs into a json response and sets the correct headers"""

        self.response.write(json.dumps(kwargs))
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(http_code, kwargs.get("message"))


    def render_xml_response(self, xml_string, http_code=200):
        """Renders kwargs into an xml response and sets the correct headers"""

        self.response.write(xml_string)
        self.response.headers["Content-Type"] = "text/xml"
        self.response.set_status(http_code)

    def render_xml_rss_response(self, xml_string, http_code=200):
        """Renders kwargs into an xml response and sets the correct headers"""

        self.response.headers["Content-Type"] = "application/rss+xml"
        self.response.set_status(http_code)
        self.response.write(xml_string)
        


    def head(self):
        # We tend to get HEAD requests, particularly from bots.
        # This is here to suppress "method not allowed" errors in the logs
        pass


    @property
    def geoip_country_code(self):
        """Returns the country code as provided by App Engine's built in geolocation"""
        return self.response.headers.get("X-AppEngine-country")
