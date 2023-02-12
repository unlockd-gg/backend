import endpoints
import logging
import uuid
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

from apps.uetopia.controllers.users import UsersController

from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.group_games import GroupGamesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ServerGameRenameHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] ServerGameRenameHandler")

        ## this is a game key
        key_id = self.request.get('key_id')

        gamesController = GamesController()
        serverController = ServersController()

        game = gamesController.get_by_key_id(int(key_id))
        if not game:
            logging.error('Game not found')
            return

        if self.request.get('cursor'):
            curs = Cursor(urlsafe=self.request.get('cursor'))
        else:
            curs = Cursor()

        servers, cursor, more  = serverController.list_page_by_gameKeyId(game.key.id(), start_cursor=curs)

        if len(servers) > 0:
            for server in servers:
                server.gameTitle = game.title

                serverController.update(server)

            if more:
                logging.info('Found more.  Re-queue the task.')

                if cursor:
                    cursor_urlsafe = cursor.urlsafe()
                else:
                    cursor_urlsafe = None

                taskUrl='/task/server/game_batch_rename'
                taskqueue.add(url=taskUrl, queue_name='gameRenameSubprocess', params={'key_id': game.key.id(), 'cursor': cursor_urlsafe })
