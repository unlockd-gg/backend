import logging
import string
import random
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.user_login_tokens import UserLoginTokens
from configuration import *

class UserLoginTokensController(BaseController):
    """Users Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = UserLoginTokens

    def get_by_userKeyId(self, userKeyId):
        """ get a record for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_list_by_userKeyId(self, userKeyId):
        """ get a record for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)

    def get_by_access_token(self, access_token):
        """ get a record by the access token """
        query = self.model.query()
        query = query.filter(self.model.access_token == access_token)
        return query.get()

    def create_unique_access_token(self, size=40, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        """ create a unique access_token """
        rebuild = True
        while rebuild:

            access_token = ''.join(random.choice(chars) for x in range(size))
            if self.get_by_access_token(access_token) == None:
                rebuild = False
        return access_token

    def get_or_create_token(self, userKeyId, access_token):
        """ check if this access token exists for this user.  If not, create it.  Delete everything else for this user """
        existing_access_tokens = self.get_list_by_userKeyId(userKeyId)
        exists = False
        e_token = None
        for existing_access_token in existing_access_tokens:
            if existing_access_token.access_token == access_token:
                logging.info('UserLoginTokensController: Token exists')
                exists = True
                e_token = existing_access_token
            else:
                logging.info('UserLoginTokensController: Incorrect token found in datastore - deleting')
                self.delete(existing_access_token)
        if not exists:
            logging.info('UserLoginTokensController: Token not found - Creating it')
            e_token = self.create(userKeyId = userKeyId,
                access_token = access_token,
                )

        return e_token
