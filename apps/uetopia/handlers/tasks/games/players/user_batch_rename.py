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
from apps.uetopia.controllers.game_players import GamePlayersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GamePlayerUserRenameHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GamePlayerUserRenameHandler")

        ## this is a user key
        key_id = self.request.get('key_id')

        userController = UsersController()

        gamePlayersController = GamePlayersController()

        user = userController.get_by_key_id(int(key_id))
        if not user:
            logging.error('User not found')
            return

        if self.request.get('cursor'):
            curs = Cursor(urlsafe=self.request.get('cursor'))
        else:
            curs = Cursor()

        gamePlayersBatch, cursor, more  = gamePlayersController.list_by_userKeyId(user.key.id(), start_cursor=curs)

        if len(gamePlayersBatch) > 0:
            for gamePlayer in gamePlayersBatch:
                gamePlayer.userTitle = user.title

                gamePlayersController.update(gamePlayer)

            if more:
                logging.info('Found more.  Re-queue the task.')

                taskUrl='/task/game/player/user_batch_rename'
                taskqueue.add(url=taskUrl, queue_name='userRenameSubprocess', params={'key_id': game.key.id(), 'cursor': curs.urlsafe()})
