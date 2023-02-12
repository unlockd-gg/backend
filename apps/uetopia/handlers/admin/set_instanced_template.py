import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.servers import ServersController
from configuration import *

class SetInstancedTemplateFlagHandler(BaseHandler):
    def get(self):
        logging.info('SetInstancedTemplateFlagHandler')

        serverController = ServersController()

        #users_with_terms_accepted, cursor, more = userController.list_by_terms_accepted()
        servers = serverController.list()

        for server in servers:
            logging.info('processing server')
            server.instanced_from_template = None

            serverController.update(server)


        return self.render_json_response(
            servers_processed = len(servers),
            #more = more
        )
