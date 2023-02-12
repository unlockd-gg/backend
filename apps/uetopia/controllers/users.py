import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.users import Users
from configuration import *

class UsersController(BaseController):
    """Users Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Users

    def get_by_googleUser(self, googleUser):
        """ get a customer account for a user """
        query = self.model.query()
        query = query.filter(self.model.googleUser == googleUser)
        return query.get()

    def get_all_by_googleUser(self, googleUser):
        """ get a customer account for a user """
        query = self.model.query()
        query = query.filter(self.model.googleUser == googleUser)
        return query.fetch(1000)

    def get_by_firebaseUser(self, firebaseUser):
        """ get a user """
        query = self.model.query()
        query = query.filter(self.model.firebaseUser == firebaseUser)
        return query.get()

    def get_all_by_firebaseUser(self, firebaseUser):
        """ get a a user """
        query = self.model.query()
        query = query.filter(self.model.firebaseUser == firebaseUser)
        return query.fetch(1000)

    def get_by_email(self, email):
        """ get a user by email """
        query = self.model.query()
        query = query.filter(self.model.email == email)
        return query.get()

    def list_by_terms_accepted(self):
        """ get all users that have accepted the terms """
        query = self.model.query()
        query = query.filter(self.model.agreed_with_terms == True)

        entities, cursor, more = query.fetch_page(100)

        return entities, cursor, more

    def get_all_by_terms_accepted(self):
        """ get all users that have accepted the terms """
        query = self.model.query()
        query = query.filter(self.model.agreed_with_terms == True)
        return query.fetch(1000)

    def get_all_by_profile_saved(self):
        """ get all users that have accepted the terms """
        query = self.model.query()
        query = query.filter(self.model.profile_saved == True)
        return query.fetch(1000)
