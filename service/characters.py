import endpoints
import logging
import uuid
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

from apps.uetopia.controllers.users import UsersController

## MODELS
from apps.uetopia.models.game_characters import *

## CONTROLLERS
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_player_snapshot import GamePlayerSnapshotController
from apps.uetopia.controllers.game_characters import GameCharactersController
from apps.uetopia.controllers.server_clusters import ServerClustersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

@endpoints.api(name="characters", version="v1", description="Characters API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE])
class CharactersApi(remote.Service):
    @endpoints.method(GAME_CHARACTER_CREATE_RESOURCE, GameCharacterResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        """ Create a new character """
        logging.info("create")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameCharacterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameCharacterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameCharacterResponse(response_message='Error: No User Record Found. ', response_successful=False)


        gamesController = GamesController()
        gamePlayerController = GamePlayersController()
        gameCharacterController = GameCharactersController()
        serverClusterController = ServerClustersController()

        if not request.gameKeyId:
            logging.info('no gameKeyId found')
            if not request.gameKeyIdStr:
                logging.info('no gameKeyIdStr found')
                return GameCharacterResponse(response_message="gameKeyId is required", response_successful=False)

        try:
            game = gamesController.get_by_key_id(int(request.gameKeyId))
        except:
            game = gamesController.get_by_key_id(int(request.gameKeyIdStr))

        if not game:
            logging.info('no game found')
            return GameCharacterResponse(response_message="game not found", response_successful=False)

        if not game.characters_enabled:
            logging.info('characters are not enabled')
            return GameCharacterResponse(response_message="characters are not enabled", response_successful=False)

        ## check count
        current_game_characters = gameCharacterController.get_list_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id() )
        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id() )

        if not game_player:
            logging.info('No game player found - creating it.')

            ## assign a random server cluster
            selected_server_cluster = serverClusterController.get_by_gameKeyId(game.key.id())
            if selected_server_cluster:
                lastServerClusterKeyId = selected_server_cluster.key.id()

            else:
                logging.info('no server cluster could be found')

                ## this is OK if the game isn't using continuous API
                if game.server_instance_continuous:
                    logging.info('continuous server API is enabled - Throwing an error')

                    return GameCharacterResponse(response_message="Continuous server API is enabled, But no server cluster could be found.", response_successful=False)

                selected_server_cluster = None
                lastServerClusterKeyId = None



            game_player = gamePlayerController.create(
                gameKeyId = game.key.id(),
                gameTitle = game.title,
                userKeyId = authorized_user.key.id(),
                userTitle = authorized_user.title,
                locked = False,
                online = True,
                rank = 1600,
                score = 0,
                #autoAuth = True,
                #autoAuthThreshold = 100000,
                autoTransfer = True,
                firebaseUser = authorized_user.firebaseUser,
                picture = authorized_user.picture,
                lastServerClusterKeyId = lastServerClusterKeyId,
                groupKeyId = authorized_user.groupTagKeyId,
                groupTag = authorized_user.groupTag,
                showGameOnProfile = True
            )

            if game.discord_subscribe_new_players and game.discord_webhook_admin:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                message = "New Player: %s | %s" % (authorized_user.key.id(), authorized_user.title)
                url = "http://ue4topia.appspot.com/#/user/%s" % authorized_user.key.id()
                discord_data = { "embeds": [{"title": "New Player", "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(game.discord_webhook_admin,
                                  "POST",
                                  data,
                                  headers=headers)


        if game_player.characterMaxAllowedCount:
            characterMaxAllowedCount = game_player.characterMaxAllowedCount
        else:
            characterMaxAllowedCount = game.character_slots_new_user_default

        if len(current_game_characters) >= characterMaxAllowedCount:
            logging.info('you are at your maximum amount of characters')

            http_auth = Http()
            headers = {"Content-Type": "application/json"}

            textMessage = "> You are at the maximum amount of characters, and cannot create more."

            chat_msg = json.dumps({"type":"chat",
                                    "textMessage":textMessage,
                                    "userKeyId": "SYSTEM",
                                    "userTitle": "SYSTEM",
                                    #"chatMessageKeyId": chatMessageKeyId,
                                    #"chatChannelTitle": channel.title,
                                    #"chatChannelKeyId": channel.key.id(),
                                    "created":datetime.datetime.now().isoformat()
            })

            # push out to in-game clients via heroku
            # ignore if it's failing
            try:
                URL = "%s/user/%s/chat/" % (HEROKU_SOCKETIO_SERVER, authorized_user.firebaseUser)
                resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  chat_msg,
                                  headers=headers)

                logging.info(resp)
                logging.info(content)
            except:
                logging.error('heroku error')

            return GameCharacterResponse(response_message="you are at your maximum amount of characters", response_successful=False)


        ## TODO don't allow if match join pending

        ## TODO - any other checks?



        new_game_character = gameCharacterController.create(
            title = request.title,
            description = request.description,
            gameKeyId = game.key.id(),
            gameTitle = game.title,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            firebaseUser = authorized_user.firebaseUser,
            characterType = request.characterType,
            characterState = request.characterState,
            characterAlive = True,
            currentlySelectedActive = True,
            characterCustom = request.characterCustom,
            rank = 1600,
            score = 0,
            experience = 0,
            level = 0
        )

        ## set the new character as selected

        game_player.characterCurrentKeyId = new_game_character.key.id()
        game_player.characterCurrentTitle = new_game_character.title

        ## also set the MaxAllowed
        game_player.characterMaxAllowedCount = characterMaxAllowedCount

        gamePlayerController.update(game_player)

        ## turn off selected on any other characters
        for current_game_character in current_game_characters:
            if current_game_character.currentlySelectedActive:
                logging.info('turning active off for previous character')
                current_game_character.currentlySelectedActive = False
                gameCharacterController.update(current_game_character)

        return GameCharacterResponse(response_message="Character Created", response_successful=True)

    @endpoints.method(GAME_CHARACTER_COLLECTION_PAGE_RESOURCE, GameCharacterCollection, path='collectionGetPage', http_method='POST', name='collection.get.page')
    def collectionGetPage(self, request):
        """ Get a collection of game characters """
        logging.info("collectionGetPage")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameCharacterCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameCharacterCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameCharacterCollection(response_message='Error: No User Record Found. ', response_successful=False)




        gamesController = GamesController()
        gameCharacterController = GameCharactersController()

        if not request.gameKeyId:
            if not request.gameKeyIdStr:
                return GameCharacterCollection(response_message="gameKeyId is required")

        try:
            game = gamesController.get_by_key_id(int(request.gameKeyId))
        except:
            game = gamesController.get_by_key_id(int(request.gameKeyIdStr))

        if not game:
            return GameCharacterCollection(response_message="game not found", response_successful=False)

        ## developer request
        if request.developerRequest:
            logging.info('developerRequest')
            if game.userKeyId != authorized_user.key.id():
                logging.info('developer mismatch')
                return GameCharacterCollection(response_message="You can only view characters in your games.", response_successful=False)

            logging.info('userKeyId: %s' % request.userKeyId)
            entities = gameCharacterController.get_list_by_gameKeyId_userKeyId(game.key.id(), request.userKeyId)
        else:
            entities = gameCharacterController.get_list_by_gameKeyId_userKeyId(game.key.id(), authorized_user.key.id())

        entity_list = []

        for entity in entities:
            entity_list.append(GameCharacterResponse(
                key_id = str(entity.key.id()),
                modified = entity.modified.isoformat(),
                title = entity.title,
                description = entity.description,
                currentlySelectedActive = entity.currentlySelectedActive,
                characterType = entity.characterType,
                characterState = entity.characterState,
                characterAlive = entity.characterAlive,
                characterCustom = entity.characterCustom,
                character = entity.character,
                rank = entity.rank,
                score = entity.score,
                level = entity.level
            ))

        response = GameCharacterCollection(
            characters = entity_list,
            mm_region = authorized_user.region,
            response_message="Success.", response_successful=True
        )

        return response

    @endpoints.method(GAME_CHARACTER_GET_RESOURCE, GameCharacterResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        """ Get a character """
        logging.info("get")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameCharacterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameCharacterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameCharacterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gamesController = GamesController()
        gameCharacterController = GameCharactersController()
        gamePlayerSnapshotController = GamePlayerSnapshotController()

        ## get the character by key
        game_character = gameCharacterController.get_by_key_id(request.gameCharacterKeyId)
        if not game_character:
            logging.info('game character not found with the supplied key')
            return GameCharacterResponse(response_message='Error: game character not found with the supplied key. ', response_successful=False)

        ## developers can get character data for thier own game
        if request.developerRequest:
            logging.info('developer request')

            game = gamesController.get_by_key_id(game_character.gameKeyId)

            if not game:
                logging.info('game not found')
                return GameCharacterResponse(response_message="game not found", response_successful=False)


            if game.userKeyId != authorized_user.key.id():
                logging.info('developer mismatch')
                return GameCharacterResponse(response_message="You can only view characters in your games.", response_successful=False)

            ## ok to return

            return GameCharacterResponse(
                    key_id = str(game_character.key.id()), ## TODO turn this back to an int
                    created = game_character.created.isoformat(),
                    #modified = game_character.modified.isoformat(),
                    rank = game_character.rank,
                    #online = game_character.online,
                    userTitle = game_character.userTitle,
                    userKeyId = game_character.userKeyId,
                    #autoAuth = game_player.autoAuth,
                    #autoAuthThreshold = game_player.autoAuthThreshold,
                    #autoTransfer = game_player.autoTransfer,
                    #gameTrustable = game.trustable,
                    lastServerClusterKeyId = game_character.lastServerClusterKeyId,

                    locked = game_character.locked,
                    locked_by_serverKeyId = game_character.locked_by_serverKeyId,
                    score = game_character.score,
                    experience = game_character.experience,
                    experienceThisLevel = game_character.experienceThisLevel,
                    level = game_character.level,
                    inventory = game_character.inventory,
                    equipment = game_character.equipment,
                    abilities = game_character.abilities,
                    interface = game_character.interface,
                    crafting = game_character.crafting,
                    recipes = game_character.recipes,
                    character = game_character.character,
                    coordLocationX = game_character.coordLocationX,
                    coordLocationY = game_character.coordLocationY,
                    coordLocationZ = game_character.coordLocationZ,
                    zoneName = game_character.zoneName,
                    zoneKey = game_character.zoneKey,
                    lastServerKeyId = game_character.lastServerKeyId,

                    title = game_character.title,

                    # developers should also get the custom data
                    characterType = game_character.characterType,
                    characterState = game_character.characterState,
                    characterAlive = game_character.characterAlive,
                    currentlySelectedActive = game_character.currentlySelectedActive,
                    characterCustom = game_character.characterCustom,

                    response_message='Success.',
                    response_successful=True)

        else:
            logging.info('normal request')

            return GameCharacterResponse(
                    key_id = str(game_character.key.id()), ## TODO turn this back to an int
                    rank = game_character.rank,
                    #online = game_character.online,
                    userTitle = game_character.userTitle,
                    userKeyId = game_character.userKeyId,
                    #autoAuth = game_player.autoAuth,
                    #autoAuthThreshold = game_player.autoAuthThreshold,
                    #autoTransfer = game_player.autoTransfer,
                    #gameTrustable = game.trustable,
                    lastServerClusterKeyId = game_character.lastServerClusterKeyId,

                    locked = game_character.locked,
                    locked_by_serverKeyId = game_character.locked_by_serverKeyId,
                    score = game_character.score,
                    experience = game_character.experience,
                    experienceThisLevel = game_character.experienceThisLevel,
                    level = game_character.level,
                    inventory = game_character.inventory,
                    equipment = game_character.equipment,
                    abilities = game_character.abilities,
                    interface = game_character.interface,
                    crafting = game_character.crafting,
                    recipes = game_character.recipes,
                    character = game_character.character,
                    coordLocationX = game_character.coordLocationX,
                    coordLocationY = game_character.coordLocationY,
                    coordLocationZ = game_character.coordLocationZ,
                    zoneName = game_character.zoneName,
                    zoneKey = game_character.zoneKey,
                    lastServerKeyId = game_character.lastServerKeyId,

                    title = game_character.title,

                    response_message='Success.',
                    response_successful=True)


    @endpoints.method(GAME_CHARACTER_UPDATE_RESOURCE, GameCharacterResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        """ Update a character - Only the game developer can do this."""
        logging.info("update")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameCharacterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameCharacterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameCharacterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gamesController = GamesController()
        gameCharacterController = GameCharactersController()

        ## get the character by key
        game_character = gameCharacterController.get_by_key_id(request.key_id)
        if not game_character:
            logging.info('game character not found with the supplied key')
            return GameCharacterResponse(response_message='Error: game character not found with the supplied key. ', response_successful=False)


        game = gamesController.get_by_key_id(game_character.gameKeyId)

        if not game:
            logging.info('game not found')
            return GameCharacterResponse(response_message="game not found", response_successful=False)


        if game.userKeyId != authorized_user.key.id():
            logging.info('developer mismatch')
            return GameCharacterResponse(response_message="You can only update characters in your games.", response_successful=False)

        ## ok to update
        game_character.rank = request.rank
        game_character.score = request.score
        game_character.experience = request.experience
        game_character.experienceThisLevel = request.experienceThisLevel
        game_character.level = request.level
        game_character.inventory = request.inventory
        game_character.equipment = request.equipment
        game_character.abilities = request.abilities
        game_character.interface = request.interface
        game_character.crafting = request.crafting
        game_character.recipes = request.recipes
        game_character.character = request.character
        game_character.coordLocationX = request.coordLocationX
        game_character.coordLocationY = request.coordLocationY
        game_character.coordLocationZ = request.coordLocationZ
        game_character.zoneName = request.zoneName
        game_character.zoneKey = request.zoneKey
        game_character.lastServerKeyId = request.lastServerKeyId
        #game_character.characterState = "customized"

        # also update the custom data
        game_character.characterType = request.characterType
        game_character.characterState = request.characterState
        game_character.characterAlive = request.characterAlive
        game_character.currentlySelectedActive = request.currentlySelectedActive
        game_character.characterCustom = request.characterCustom

        gameCharacterController.update(game_character)

        return GameCharacterResponse(
                response_message='Success.',
                response_successful=True)




    @endpoints.method(GAME_CHARACTER_GET_RESOURCE, GameCharacterResponse, path='delete', http_method='POST', name='delete')
    def delete(self, request):
        """ Delete a game character """
        logging.info("delete")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameCharacterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameCharacterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameCharacterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        ## ONLY allow this from authorized domains
        #request_origin = self.request_state.headers['origin']
        #logging.info("request_origin: %s" %request_origin)
        #if request_origin not in RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS:
        #    logging.warning("Attempt to access a protected API endpoint from an unauthorized origin")
        #    return GameCharacterResponse(response_message='Error: This domain is not authorized to access this API endpoint ', response_successful=False)

        gameCharacterController = GameCharactersController()
        gamePlayerController = GamePlayersController()

        if not request.key_id:
            logging.info('key_id is required')
            return GameCharacterResponse(response_message="key_id is required", response_successful=False)

        entity = gameCharacterController.get_by_key_id(int(request.key_id))

        if not entity.userKeyId == authorized_user.key.id():
            logging.info('only the characters owner can delete it')
            return GameCharacterResponse(response_message="only the character's owner can delete it", response_successful=False)

        ## check to see if it is currently selected in the game player
        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(entity.gameKeyId, authorized_user.key.id() )
        if game_player.characterCurrentKeyId == entity.key.id():
            logging.info('you cannot delete your active character. ')
            return GameCharacterResponse(response_message="you cannot delete your active character. ", response_successful=False)

        ## TODO  - any other checks?

        gameCharacterController.delete(entity)

        response = GameCharacterResponse(
            response_message='Success.  Character deleted.',
            response_successful=True
        )

        return response

    @endpoints.method(GAME_CHARACTER_GET_RESOURCE, GameCharacterResponse, path='select', http_method='POST', name='select')
    def select(self, request):
        """ Select a game character """
        logging.info("select")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-uetopia-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return GameCharacterResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return GameCharacterResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return GameCharacterResponse(response_message='Error: No User Record Found. ', response_successful=False)

        gameCharacterController = GameCharactersController()
        gamePlayerController = GamePlayersController()

        if not request.key_id:
            logging.info('key_id is required')
            return GameCharacterResponse(response_message="key_id is required", response_successful=False)

        entity = gameCharacterController.get_by_key_id(int(request.key_id))

        if not entity.userKeyId == authorized_user.key.id():
            logging.info('only the characters owner can select it')
            return GameCharacterResponse(response_message="only the character's owner can select it", response_successful=False)

        ## make sure it is alive
        if not entity.characterAlive:
            logging.info('dead characters cannot be selected')
            return GameCharacterResponse(response_message="dead characters cannot be selected", response_successful=False)

        ## check to see if it is currently selected in the game player
        game_player = gamePlayerController.get_by_gameKeyId_userKeyId(entity.gameKeyId, authorized_user.key.id() )
        if game_player.characterCurrentKeyId == entity.key.id():
            logging.info('This character is already selected. ')

            ## reset the flag - just in case
            entity.currentlySelectedActive = True
            gameCharacterController.update(entity)

            return GameCharacterResponse(response_message="This character is already selected. ", response_successful=False)

        ## get the previously selected character
        previous_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
        if previous_character:
            previous_character.currentlySelectedActive = False
            gameCharacterController.update(previous_character)

        ## TODO  - don't allow if match join pending

        ## TODO  - any other checks?

        game_player.characterCurrentKeyId = entity.key.id()
        game_player.characterCurrentTitle = entity.title

        gamePlayerController.update(game_player)

        entity.currentlySelectedActive = True
        gameCharacterController.update(entity)

        response = GameCharacterResponse(
            response_message='Success.  Character selected.',
            response_successful=True
        )

        return response
