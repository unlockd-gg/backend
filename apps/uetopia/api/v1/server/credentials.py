import logging
import datetime
import string
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from configuration import *

class CredentialsHandler(BaseHandler):
    def post(self):
        """
        Send server credentials.  Uses game key/secret for auth
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, serverKey
        """

        serverController = ServersController()
        gameController = GamesController()

        logging.info(self.request)


        ##try:
        game = gameController.verify_signed_auth(self.request)
        ##except:
        ##    game = False

        if not game: # == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False,
                serverAPIKey = None,
            )
        else:
            logging.info('auth success')

            serverKeyId = self.request.get('serverKeyId', None)
            if not serverKeyId:
                logging.info('serverKeyId not found')
                return self.render_json_response(
                    authorization = True,
                    error = "serverKeyId not found"
                )

            logging.info(serverKeyId)

            server = serverController.get_by_key_id(int(serverKeyId))
            if not server:
                logging.info('server not found')
                return self.render_json_response(
                    authorization = True,
                    error = "server not found"
                )

            if game.key.id() != server.gameKeyId:
                logging.info('server does not belong to this game')
                return self.render_json_response(
                    authorization = True,
                    error = "server does not belong to this game"
                )


            return self.render_json_response(
                authorization = True,
                serverAPIKey = server.apiKey,
                serverAPISecret = server.apiSecret
            )
