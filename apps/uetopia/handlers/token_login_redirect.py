import logging
from apps.handlers import BaseHandler
from google.appengine.api import users
from apps.uetopia.controllers.users import UsersController

class TokenLoginRedirectHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def get(self):
        """ Static Index

        """
        logging.info('redirecting')

        redirect_uri = '/4.16/t_login_complete?state=%s&access_token=%s' %(self.request.get('state'),self.request.get('access_token') )

        return self.redirect(redirect_uri)
