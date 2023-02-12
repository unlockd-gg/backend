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

#from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.badges import BadgesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class GamePlayerUpdateTagsHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] GamePlayerUpdateTagsHandler")

        ## this is a game_player key
        key_id = self.request.get('key_id')

        gamePlayerController = GamePlayersController()

        entity = gamePlayerController.get_by_key_id(int(key_id))
        if not entity:
            logging.error('Game Player not found')
            return

        ## get the active badges for this game player
        badgeController = BadgesController()

        game_player_badges = badgeController.get_active_by_gameKeyId_userKeyId(entity.gameKeyId, entity.userKeyId)

        all_tags = []

        for gp_badge in game_player_badges:
            logging.info('found badge')

            for gp_badge_tag in gp_badge.tags:
                logging.info('found tag')

                if gp_badge_tag not in all_tags:
                    logging.info('adding this tag')

                    all_tags.append(gp_badge_tag)

        entity.badgeTags = all_tags
        gamePlayerController.update(entity)

        return
