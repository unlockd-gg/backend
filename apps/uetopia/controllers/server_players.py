import datetime
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.server_players import ServerPlayers

class ServerPlayersController(BaseController):
    """Server Players Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = ServerPlayers

    def get_server_user(self, serverKeyId, userKeyId):
        """ get a pending user authorization """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_server_user_by_platformid(self, serverKeyId, userKeyId):
        """ get a pending user authorization """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.get()

    def get_list_by_server(self, serverKeyId):
        """ get the list for a user """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        return query.fetch(1000)

    def get_list_by_user(self, userKeyId):
        """ get the list for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(1000)

    def get_list_by_user_not_matchmaker(self, userKeyId):
        """ get the list for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        #query = query.filter(self.model.internal_matchmaker == False)
        return query.fetch(100)

    def get_authorized_list_by_user(self, userKeyId):
        """ get the list for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.authorized == True)
        return query.fetch(1000)

    def get_list_authorized_by_server(self, serverKeyId):
        """ get all of the server's auths """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.authorized == True)
        return query.fetch(1000)

    def get_list_ladderrank_by_server(self, serverKeyId, limit=20):
        """ get all of the server's auths """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.order(-self.model.ladderRank)
        return query.fetch(limit)


    def get_pending_authorization(self, serverKeyId, userKeyId):
        """ get a pending user authorization """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.pending_authorize == True)
        return query.get()

    def get_pending_deauthorization(self, serverKeyId, userKeyId):
        """ get a pending user authorization """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.pending_deauthorize == True)
        return query.get()

    def get_pending_authorizations(self, serverKeyId):
        """ get all of the server's pending auths """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.pending_authorize == True)
        return query.fetch(1000)

    def get_pending_deauthorizations(self, serverKeyId):
        """ get all of the server's pending deauths """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.pending_deauthorize == True)
        return query.fetch(1000)

    def get_non_matchmaker_list_by_user(self, userKeyId):
        """ get the list for a user """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        #query = query.filter(self.model.internal_matchmaker == False)
        return query.fetch(1000)

    def get_list_active_by_server(self, serverKeyId):
        """ get all of the server's auths """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.active == True)
        return query.fetch(1000)

    def get_list_truncated_by_server(self, serverKeyId, modifiedDate, limit):
        """ get a truncated list of server user members sorted by modified """
        query = self.model.query()
        query = query.filter(self.model.serverKeyId == serverKeyId)
        query = query.filter(self.model.modified >= modifiedDate)
        query = query.order(-self.model.modified)
        return query.fetch(limit)

    def get_active_stale(self, modifiedDate):
        """ get user connections that are active and modified earler than the supplied date """
        query = self.model.query()
        query = query.filter(self.model.active == True)
        query = query.filter(self.model.modified < modifiedDate)
        return query.fetch(1000)

    def get_active_recent_by_userKey(self, modifiedDate, userKeyId):
        """ get user connections that are active and modified earler than the supplied date """
        query = self.model.query()
        query = query.filter(self.model.active == True)
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.modified < modifiedDate)
        return query.fetch(10)

    def get_most_recently_used_shards_by_userKeyId(self, serverShardKeyId, userKeyId):
        """ get most recently used shards """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.serverShardKeyId == serverShardKeyId)
        query = query.order(-self.model.modified)
        return query.fetch(10)
