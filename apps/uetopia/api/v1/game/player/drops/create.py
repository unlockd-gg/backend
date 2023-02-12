import logging
import datetime
import string
import json
import dateutil.parser
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController
from apps.uetopia.controllers.drops import DropsController
from configuration import *

class createDropHandler(BaseHandler):
    def post(self, gamePlayerKeyId):
        """
        Begin a match
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, attackingPlayerKeyId, defendingPlayerKeyId, gameModeKeyId, region, metaMatchKeyId
        """

        ucontroller = UsersController()

        gameController = GamesController()
        serverController = ServersController()

        gamePlayerController = GamePlayersController()
        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()

        dropsController = DropsController()

        try:
            game = gameController.verify_signed_auth(self.request)
        except:
            game = False

        if game == False:
            logging.info('game auth failure')

            ## also try authentication as server.  This might be coming from a server loot process.  If a user does not have enough inventory space, a drop will be created instead.
            try:
                server = serverController.verify_signed_auth(self.request)
            except:
                server = False

            if server == False:
                logging.info('server auth failure')

                return self.render_json_response(
                    authorization = False,
                    request_successful = False
                )
            else:
                logging.info('server auth success')
                game = gameController.get_by_key_id(server.gameKeyId)
        else:
            logging.info('game auth success')

        logging.info(self.request)

        ## the game has auth so just make the drop.

        ## parse or create - possibly missing datetime
        now = datetime.datetime.now()
        thirty_days = datetime.timedelta(days=30)
        thirty_days_from_now = now + thirty_days

        ## parse the incoming json
        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        if 'expirationDate' in jsonobject :
            logging.info('found expiration date')

            try:
                expirationDate = dateutil.parser.parse(jsonobject['expirationDate'])
            except:
                expirationDate = thirty_days_from_now
        else:
            expirationDate = thirty_days_from_now

        # get the game player
        game_player = gamePlayerController.get_by_key_id(int(gamePlayerKeyId))
        if not game_player:
            logging.info('game player not found')
            return self.render_json_response(
                authorization = True,
                request_successful = False,
                request_message="No Game player found for this user"
            )

        ## get the user
        intended_recipient = ucontroller.get_by_key_id(game_player.userKeyId)

        if not intended_recipient:
            logging.info('user not found')
            return self.render_json_response(
                authorization = True,
                request_successful = False,
                request_message="No User found with the supplied Key"
            )

        try:
            tier = jsonobject['Tier']
            logging.info(tier)
        except:
            tier = 0




        dropsController.create(
            expirationDate = expirationDate,
            title = jsonobject['title'],
            description = jsonobject['description'],
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            userKeyId = intended_recipient.key.id(),
            #userTitle = ndb.StringProperty(indexed=False)

            gamePlayerKeyId = game_player.key.id(),
            #gamePlayerTitle = ndb.StringProperty(indexed=False)

            uiIcon = jsonobject['uiIcon'],
            data = jsonobject['data'],
            tier = tier
        )

        return self.render_json_response(
            authorization = True,
            request_successful = True,
            request_message="Drop Created"
        )
