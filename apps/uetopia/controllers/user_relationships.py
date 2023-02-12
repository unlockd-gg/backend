import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.user_relationships import UserRelationships
from configuration import *

class UserRelationshipsController(BaseController):
    """UserRelationships Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = UserRelationships

    def get_by_userKeyId(self, userKeyId):
        """ get friends for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(100)

    def get_list_by_userTargetKeyId(self,userTargetKeyId):
        """ get relationships for a user """
        query = self.model.query()
        query = query.filter(self.model.userTargetKeyId == userTargetKeyId)
        return query.fetch(100)

    def get_by_userKeyId_userTargetKeyId(self,userKeyId, userTargetKeyId):
        """ get relationship for two users """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.userTargetKeyId == userTargetKeyId)
        return query.get()

    def get_list_confirmed_by_userTargetKeyId(self,userTargetKeyId):
        """ get confirmed relationships for a user """
        query = self.model.query()
        query = query.filter(self.model.userTargetKeyId == userTargetKeyId)
        query = query.filter(self.model.friendConfirmed == True)
        return query.fetch(100)
