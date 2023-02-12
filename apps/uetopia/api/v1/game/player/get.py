import logging
import datetime
import string
from apps.handlers import BaseHandler
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.game_characters import GameCharactersController

from apps.uetopia.controllers.group_roles import GroupRolesController
from apps.uetopia.controllers.group_users import GroupUsersController
from apps.uetopia.controllers.match import MatchController

from configuration import *

class gamePlayerGetHandler(BaseHandler):
    def post(self, gamePlayerKeyId):
        """
        Send game player
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        Optional parameters:  lock
        """

        ## This request could be coming in from a server
        ## OR, a match...
        ## we need to check for both.

        serverController = ServersController()
        ucontroller = UsersController()
        #spController = ServerPlayersController()
        #pspController = PendingServerPlayersController()
        gpController = GamePlayersController()
        gameCharacterController = GameCharactersController()
        gameController = GamesController()
        groupRolesController = GroupRolesController()
        groupUsersController = GroupUsersController()
        matchController = MatchController()

        try:
            server = serverController.verify_signed_auth(self.request)
        except:
            server = False

        game = None

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
                authorization = False
            )



        game_player = gpController.get_by_key_id(int(gamePlayerKeyId))
        if not game_player:
            logging.info('game player not found')
            return self.render_json_response(
                authorization = True,
                error= "The game user was not found."
                )

        logging.info(game_player)

        ## check for drop/pickup permissions for this user
        ## in the case of a group instance this is determined by permissions
        ## private instance - the owner should be the only user allowed, so always true/true
        ## dungeon instance - games might spawn loot here, so pickup true, drop false
        ## otherwise check the server itself.  Some levels might not want users dropping stuff.

        player_can_pickup = False
        player_can_drop = False
        ## just keeping track of these so we can skip the second lookup
        group_user = None
        group_role = None

        if server:
            if server.drop_items_permitted:
                logging.info('server set to drop_items_permitted')
                if server.instanced_from_template and server.instance_server_configuration == "group":
                    logging.info('this is a group instance - checking user permissions')
                    group_user = groupUsersController.get_by_groupKeyId_userKeyId(server.instanced_for_groupKeyId, game_player.userKeyId)
                    if group_user:
                        logging.info('found group user')
                        group_role = groupRolesController.get_by_key_id(group_user.roleKeyId)
                        if group_role:
                            logging.info('found group role')
                            if group_role.drop_items_in_group_servers:
                                logging.info('group role has permission to drop items')
                                player_can_drop = True
                else:
                    logging.info('not a group instance - allowing drop')
                    player_can_drop = True

            if server.pickup_items_permitted:
                logging.info('server set to pickup_items_permitted')
                if server.instanced_from_template and server.instance_server_configuration == "group":
                    logging.info('this is a group instance - checking user permissions')
                    if not group_user:
                        group_user = groupUsersController.get_by_groupKeyId_userKeyId(server.instanced_for_groupKeyId, game_player.userKeyId)
                    if group_user:
                        logging.info('found group user')
                        if not group_role:
                            group_role = groupRolesController.get_by_key_id(group_user.roleKeyId)
                        if group_role:
                            logging.info('found group role')
                            if group_role.pickup_items_in_group_servers:
                                logging.info('group role has permission to pickup items')
                                player_can_pickup = True
                else:
                    logging.info('not a group instance - allowing pickup')
                    player_can_pickup = True


        if game.enforce_locks:
            logging.info('Game settings are set to ENFORCE LOCKS')

            lock = self.request.get('lock', False)

            if lock:
                if game_player.locked:
                    if game_player.locked_by_serverKeyId != server.key.id():
                        logging.info("This game player is already locked.")

                        ## TODO - discord push to game admin


                        return self.render_json_response(
                            authorization = True,
                            error= "This game player is already locked.",
                            userKeyId = str(game_player.userKeyId),
                            )
                else:
                    game_player.locked = True
                    game_player.lock_timestamp = datetime.datetime.now()
                    game_player.locked_by_serverKeyId = server.key.id()

                    gpController.update(game_player)

        ## check for character support
        if game.characters_enabled:
            logging.info('game characters are enabled')
            if game_player.characterCurrentKeyId:
                logging.info('found current active character')

                game_character = gameCharacterController.get_by_key_id(game_player.characterCurrentKeyId)
                if game_character:
                    ## Set up title with tag
                    if game_player.groupTag:
                        character_title = game_player.groupTag + " " + game_character.title
                    else:
                        character_title = game_character.title
                    ## return this character
                    return self.render_json_response(
                        authorization = True,
                        gamePlayerKeyId = str(game_player.key.id()),
                        online = game_character.online,
                        rank = game_character.rank,
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
                        userKeyId = str(game_character.userKeyId),
                        userTitle = character_title,
                        # character custom fields
                        characterCurrentKeyId = str(game_player.characterCurrentKeyId),
                        characterCurrentTitle = game_player.characterCurrentTitle,
                        characterType = game_character.characterType,
                        characterState = game_character.characterState,
                        characterAlive = game_character.characterAlive,
                        currentlySelectedActive = game_character.currentlySelectedActive,
                        characterCustom = game_character.characterCustom,
                        # calculated flags
                        allowPickup = player_can_pickup,
                        allowDrop = player_can_drop,
                        badgeTags = game_player.badgeTags
                    )
                else:
                    logging.info('selected character not found.')
                    ## TODO - hopefully this does not happen

            else:
                logging.info('no character selected')
                ## what TODO here....  make a new one?
        else:
            logging.info('game characters are disabled')

            return self.render_json_response(
                authorization = True,
                gamePlayerKeyId = str(game_player.key.id()),
                online = game_player.online,
                rank = game_player.rank,
                score = game_player.score,
                experience = game_player.experience,
                experienceThisLevel = game_player.experienceThisLevel,
                level = game_player.level,
                inventory = game_player.inventory,
                equipment = game_player.equipment,
                abilities = game_player.abilities,
                interface = game_player.interface,
                crafting = game_player.crafting,
                recipes = game_player.recipes,
                character = game_player.character,
                coordLocationX = game_player.coordLocationX,
                coordLocationY = game_player.coordLocationY,
                coordLocationZ = game_player.coordLocationZ,
                zoneName = game_player.zoneName,
                zoneKey = game_player.zoneKey,
                userKeyId = str(game_player.userKeyId),
                userTitle = game_player.userTitle,
                allowPickup = player_can_pickup,
                allowDrop = player_can_drop,
                badgeTags = game_player.badgeTags
            )
