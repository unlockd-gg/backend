import logging
import hashlib
import hmac
import urllib
import datetime
import random
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.servers import Servers
from collections import OrderedDict

class ServersController(BaseController):
    """Servers Controller"""
    def __init__(self):
        self._default_order = 'created'
        self.model = Servers

    def get_by_gamekeyid(self, gameKeyId):
        """ get a server list by game key """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        return query.fetch(1000)

    def get_by_userKeyId(self, userKeyId):
        """ get a server list by game key """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)

    def get_visible_by_game_key_id(self, gameKeyId):
        """ get a server list by game key """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.invisible_developer_setting == False)
        return query.fetch(1000)

    def get_provisioned_by_game_key_id(self, gameKeyId):
        """ get provisioned continuous servers """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.invisible_developer_setting == False)
        query = query.filter(self.model.continuous_server_provisioned == True)
        return query.fetch(10)

    def get_provisioned_by_gameKeyId_serverClusterKeyId(self, gameKeyId, serverClusterKeyId):
        """ get provisioned continuous servers """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        #query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.invisible_developer_setting == False)
        query = query.filter(self.model.continuous_server_provisioned == True)
        return query.fetch(10)

    def get_not_provisioned_entry_by_game_key_id(self, gameKeyId):
        """ get an entry server that is not provisioned """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.invisible_developer_setting == False)
        query = query.filter(self.model.continuous_server_provisioned == False)
        query = query.filter(self.model.continuous_server_entry == True)
        return query.get()

    def get_random_entry_by_gameKeyId_serverClusterKeyId(self, gameKeyId, serverClusterKeyId):
        """ get a random entry server """
        randomseed = random.random()
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.invisible_developer_setting == False)
        query = query.filter(self.model.randomRef > randomseed)
        query = query.filter(self.model.continuous_server_entry == True)
        query = query.order(-self.model.randomRef)
        return query.get()


    def get_visible(self):
        """ get a server list by game key """
        query = self.model.query()
        query = query.filter(self.model.invisible == False)
        query = query.filter(self.model.invisible_developer_setting == False)
        return query.fetch(1000)

    def get_unpaid(self):
        """ get a server list that needs payment """
        query = self.model.query()
        query = query.filter(self.model.serverAdminPaid == False)
        return query.fetch(1000)

    def get_next_unpaid(self):
        """ get a server that needs payment """
        query = self.model.query()
        query = query.filter(self.model.serverAdminPaid == False)
        return query.get()

    def get_unpaid_for_userKeyId(self, userKeyId):
        """ get a server list that needs payment """
        query = self.model.query()
        query = query.filter(self.model.serverAdminPaid == False)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(10)

    def get_visible_by_groupKeyId(self, groupKeyId):
        """ get a server list by group key """
        query = self.model.query()
        query = query.filter(self.model.groupKeyId == groupKeyId)
        query = query.filter(self.model.groupInvisible == False)

        return query.fetch(1000)



    def list_page_by_serverClusterKeyId(self, serverClusterKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_not_instanced_by_serverClusterKeyId(self, serverClusterKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.instanced_from_template == None)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_sharded_server_template_serverClusterKeyId(self, serverClusterKeyId):
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.sharded_server_template == True)
        return query.fetch(1000)

    def list_page_by_gameKeyId(self, gameKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def get_any_server_to_game_transfer_exceeded(self):
        query = self.model.query()
        query = query.filter(self.model.server_to_game_transfer_exceeded == True)
        return query.get()

    def get_by_gameKeyId_serverClusterKeyId_instanced_for_userKeyId(self, gameKeyId, serverClusterKeyId, instanced_for_userKeyId):
        """ get an entry server that is not provisioned """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.instanced_for_userKeyId == instanced_for_userKeyId)
        return query.get()

    def get_by_gameKeyId_serverClusterKeyId_instanced_for_partyKeyId(self, gameKeyId, serverClusterKeyId, instanced_for_partyKeyId):
        """ get an entry server that is not provisioned """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.instanced_for_partyKeyId == instanced_for_partyKeyId)
        return query.get()

    def get_by_gameKeyId_serverClusterKeyId_instanced_for_groupKeyId(self, gameKeyId, serverClusterKeyId, instanced_for_groupKeyId):
        """ get an entry server that is not provisioned """
        query = self.model.query()
        query = query.filter(self.model.gameKeyId == gameKeyId)
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.instanced_for_groupKeyId == instanced_for_groupKeyId)
        return query.get()

    def list_page_by_instanced_from_template_serverKeyId(self, instanced_from_template_serverKeyId, page_size=100, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.instanced_from_template_serverKeyId == instanced_from_template_serverKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_not_instanced_sharded_by_serverClusterKeyId(self, serverClusterKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.serverClusterKeyId == serverClusterKeyId)
        query = query.filter(self.model.instanced_from_template == None)
        query = query.filter(self.model.sharded_from_template != True)
        query = query.order(self.model.sharded_from_template)
        query = query.order(self.model.key)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_by_sharded_from_template_serverKeyId(self, sharded_from_template_serverKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.sharded_from_template_serverKeyId == sharded_from_template_serverKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_page_by_instanced_from_template_serverKeyId(self, instanced_from_template_serverKeyId, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.instanced_from_template_serverKeyId == instanced_from_template_serverKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more
