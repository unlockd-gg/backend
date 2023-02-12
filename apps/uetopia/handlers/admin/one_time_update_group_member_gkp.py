import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.group_users import GroupUsersController
from configuration import *

class UpdateGroupMemberGkpHandler(BaseHandler):
    def get(self):
        logging.info('UpdateGroupMemberGkpHandler')

        groupUserController = GroupUsersController()

        #users_with_terms_accepted, cursor, more = userController.list_by_terms_accepted()
        g_users = groupUserController.list()

        for g_user in g_users:
            logging.info('processing g user')
            g_user.vettingEnabled = True
            g_user.vettingCompleted = False
            g_user.vettingFinalized = False

            g_user.gkpAmount = 0.0
            g_user.gkpVettingRemaining = 4

            groupUserController.update(g_user)


        return self.render_json_response(
            g_users_processed = len(g_users),
            #more = more
        )
