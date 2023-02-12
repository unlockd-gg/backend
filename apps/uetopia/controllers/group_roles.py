import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.group_roles import GroupRoles

class GroupRolesController(BaseController):
    """Group Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = GroupRoles

    def get_by_groupKeyId(self, groupKeyId):
        """ get all for a slugifyUrl """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        #query = query.order(self.model.created)
        return query.fetch(100)

    def get_by_groupKeyId_applicant_role(self, groupKeyId):
        """ get the applicant role for a group """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.applicant_role == True)
        return query.get()
