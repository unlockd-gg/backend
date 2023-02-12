import logging
import datetime
import string
import json
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.game_player_snapshot import GamePlayerSnapshotController
from apps.uetopia.utilities.game_player_snapshot import create_game_player_snapshot
from apps.uetopia.controllers.match import MatchController
from configuration import *

class gamePlayerUpdateHandler(BaseHandler):
    def post(self, gamePlayerKeyId):
        """
        Send game player
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        Optional parameters:  unlock
        """

        ## This request could be coming in from a server
        ## OR, a match...
        ## we need to check for both.

        serverController = ServersController()
        ucontroller = UsersController()
        gpController = GamePlayersController()
        gameController = GamesController()
        gameCharacterController = GameCharactersController()
        #gamePlayerSnapshotController = GamePlayerSnapshotController()

        matchController = MatchController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        game = None
        match = None

        if server:
            logging.info('auth success')
            game = gameController.get_by_key_id(server.gameKeyId)

        else:
            logging.info('auth failure using server')

            match = matchController.verify_signed_auth(self.request)

            if match:
                logging.info('auth success using match')
                game = gameController.get_by_key_id(match.gameKeyId)

        if not game:
            logging.info('game not found')
            return self.render_json_response(
                authorization = True,
                error= "The game was not found."
                )

        game_player = gpController.get_by_key_id(int(gamePlayerKeyId))
        if not game_player:
            logging.info("The game player was not found.")
            return self.render_json_response(
                authorization = True,
                error= "The game player was not found."
                )

        if server:
            if game.enforce_locks:
                logging.info('Game settings are set to ENFORCE LOCKS')
                if game_player.locked:
                    if game_player.locked_by_serverKeyId != server.key.id():
                        logging.info("This game player is locked by a different server.")
                        return self.render_json_response(
                            authorization = True,
                            error= "This game player is locked by a different server."
                            )

        ## parse the incoming json
        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)
        ## encryption = jsonobject["encryption"]

        if 'unlock' in jsonobject:
            logging.info('Found Unlock in json')
            unlock = jsonobject['unlock']
        else:
            logging.info('Unlock not found in json - defaulting to True')
            unlock = True

        if unlock:
            game_player.locked = False
            game_player.locked_by_serverKey = None

        ## check for character support
        if game.characters_enabled:
            logging.info('game characters are enabled')
            if game_player.characterCurrentKeyId:
                logging.info('found current active character')

                game_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
                if game_character:
                    logging.info('found game character')

                    ## update this character

                    ## deal with possible null ints
                    if not game_character.experience:
                        game_character.experience = 0;
                    if not game_character.experienceThisLevel:
                        game_character.experienceThisLevel = 0;
                    if not game_character.level:
                        game_character.level = 0;

                    if not match:
                        logging.info('Not coming from match, updating rank, score')
                        if 'rank' in jsonobject:
                            logging.info("Found rank in json")
                            game_character.rank = int(jsonobject['rank'])
                        if 'score' in jsonobject:
                            logging.info("Found score in json")
                            game_character.score = int(jsonobject['score'])

                    if 'experience' in jsonobject:
                        logging.info("Found experience in json")
                        game_character.experience = int(jsonobject['experience'])
                    if 'experienceThisLevel' in jsonobject:
                        logging.info("Found experienceThisLevel in json")
                        game_character.experienceThisLevel = int(jsonobject['experienceThisLevel'])
                    if 'level' in jsonobject:
                        logging.info("Found level in json")
                        game_character.level = int(jsonobject['level'])
                    if 'inventory' in jsonobject:
                        logging.info("Found inventory in json")
                        game_character.inventory = jsonobject['inventory']
                    if 'equipment' in jsonobject:
                        logging.info("Found equipment in json")
                        game_character.equipment = jsonobject['equipment']
                    if 'abilities' in jsonobject:
                        logging.info("Found abilities in json")
                        game_character.abilities = jsonobject['abilities']
                    if 'interface' in jsonobject:
                        logging.info("Found interface in json")
                        game_character.interface = jsonobject['interface']

                    if 'crafting' in jsonobject:
                        logging.info("Found crafting in json")
                        game_character.crafting = jsonobject['crafting']
                    if 'recipes' in jsonobject:
                        logging.info("Found recipes in json")
                        game_character.recipes = jsonobject['recipes']
                    if 'character' in jsonobject:
                        logging.info("Found character in json")
                        game_character.character = jsonobject['character']


                    if 'coordLocationX' in jsonobject:
                        logging.info("Found coordLocationX in json")
                        game_character.coordLocationX = float(jsonobject['coordLocationX'])
                    if 'coordLocationY' in jsonobject:
                        logging.info("Found coordLocationY in json")
                        game_character.coordLocationY = float(jsonobject['coordLocationY'])
                    if 'coordLocationZ' in jsonobject:
                        logging.info("Found coordLocationZ in json")
                        game_character.coordLocationZ = float(jsonobject['coordLocationZ'])
                    if 'zoneName' in jsonobject:
                        logging.info("Found zoneName in json")
                        game_character.zoneName = jsonobject['zoneName']
                    if 'zoneKey' in jsonobject:
                        logging.info("Found zoneKey in json")
                        game_character.zoneKey = jsonobject['zoneKey']


                    # new char customization fields need update if they exist
                    if 'characterType' in jsonobject:
                        logging.info("Found characterType in json")
                        game_character.characterType = jsonobject['characterType']

                    if 'characterState' in jsonobject:
                        logging.info("Found characterState in json")
                        game_character.characterState = jsonobject['characterState']

                    if 'characterAlive' in jsonobject:
                        logging.info("Found characterAlive in json")
                        game_character.characterAlive = jsonobject['characterAlive']

                    if 'currentlySelectedActive' in jsonobject:
                        logging.info("Found currentlySelectedActive in json")
                        game_character.currentlySelectedActive = jsonobject['currentlySelectedActive']

                    if 'characterCustom' in jsonobject:
                        logging.info("Found characterCustom in json")
                        game_character.characterCustom = jsonobject['characterCustom']

                    if server:
                        game_character.lastServerClusterKeyId = server.serverClusterKeyId
                        game_character.lastServerKeyId = server.key.id()



                    gameCharacterController.update(game_character)
                    gpController.update(game_player)

                    ## Create a snapshot
                    #gamePlayerSnapshotController.create(**game_player.to_dict())
                    player_snapshot = create_game_player_snapshot(game_player, gamePlayerKeyId=game_player.key.id())
                    character_snapshot = create_game_player_snapshot(game_character, characterKeyId=game_character.key.id())
                else:
                    logging.info('could not find game character')
            else:
                logging.info('no character key found')

        else:

            ## deal with possible null ints
            if not game_player.experience:
                game_player.experience = 0;
            if not game_player.experienceThisLevel:
                game_player.experienceThisLevel = 0;
            if not game_player.level:
                game_player.level = 0;


            if 'rank' in jsonobject:
                logging.info("Found rank in json")
                game_player.rank = int(jsonobject['rank'])
            if 'score' in jsonobject:
                logging.info("Found score in json")
                game_player.score = int(jsonobject['score'])
            if 'experience' in jsonobject:
                logging.info("Found experience in json")
                game_player.experience = int(jsonobject['experience'])
            if 'experienceThisLevel' in jsonobject:
                logging.info("Found experienceThisLevel in json")
                game_player.experienceThisLevel = int(jsonobject['experienceThisLevel'])
            if 'level' in jsonobject:
                logging.info("Found level in json")
                game_player.level = int(jsonobject['level'])
            if 'inventory' in jsonobject:
                logging.info("Found inventory in json")
                game_player.inventory = jsonobject['inventory']
            if 'equipment' in jsonobject:
                logging.info("Found equipment in json")
                game_player.equipment = jsonobject['equipment']
            if 'abilities' in jsonobject:
                logging.info("Found abilities in json")
                game_player.abilities = jsonobject['abilities']
            if 'interface' in jsonobject:
                logging.info("Found interface in json")
                game_player.interface = jsonobject['interface']

            if 'crafting' in jsonobject:
                logging.info("Found crafting in json")
                game_player.crafting = jsonobject['crafting']
            if 'recipes' in jsonobject:
                logging.info("Found recipes in json")
                game_player.recipes = jsonobject['recipes']
            if 'character' in jsonobject:
                logging.info("Found character in json")
                game_player.character = jsonobject['character']

            if 'coordLocationX' in jsonobject:
                logging.info("Found coordLocationX in json")
                game_player.coordLocationX = float(jsonobject['coordLocationX'])
            if 'coordLocationY' in jsonobject:
                logging.info("Found coordLocationY in json")
                game_player.coordLocationY = float(jsonobject['coordLocationY'])
            if 'coordLocationZ' in jsonobject:
                logging.info("Found coordLocationZ in json")
                game_player.coordLocationZ = float(jsonobject['coordLocationZ'])
            if 'zoneName' in jsonobject:
                logging.info("Found zoneName in json")
                game_player.zoneName = jsonobject['zoneName']
            if 'zoneKey' in jsonobject:
                logging.info("Found zoneKey in json")
                game_player.zoneKey = jsonobject['zoneKey']

        if server:
            game_player.lastServerClusterKeyId = server.serverClusterKeyId
            game_player.lastServerKeyId = server.key.id()

        gpController.update(game_player)

        ## Create a snapshot
        #gamePlayerSnapshotController.create(**game_player.to_dict())
        player_snapshot = create_game_player_snapshot(game_player, gamePlayerKeyId=game_player.key.id())

        ## update firebase

        taskUrl='/task/game/player/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': game_player.key.id()}, countdown = 2,)


        return self.render_json_response(
            authorization = True,
            success=True
        )
