import logging
import random
from apps.uetopia.controllers.game_player_snapshot import GamePlayerSnapshotController

def create_game_player_snapshot(game_player, gamePlayerKeyId=None, characterKeyId=None):
    """ Copy all of the game player data into a new snapshot record """

    gamePlayerSnapshotController = GamePlayerSnapshotController()

    if gamePlayerKeyId:
        player = True
        title = None
    else:
        player = False

    if characterKeyId:
        characterRecord = True
        title = game_player.title ## when coming in via character, this is a gameplayerCharacter.
    else:
        characterRecord = False

    snapshot = gamePlayerSnapshotController.create(
        characterRecord = characterRecord,
        characterKeyId = characterKeyId,
        player = player,
        title = title,
        gamePlayerKeyId = gamePlayerKeyId,
        gameKeyId = game_player.gameKeyId,
        gameTitle = game_player.gameTitle,
        userKeyId = game_player.userKeyId,
        userTitle = game_player.userTitle,

        groupKeyId = game_player.groupKeyId,
        groupTag = game_player.groupTag,

        firebaseUser = game_player.firebaseUser,

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

        lastServerClusterKeyId = game_player.lastServerClusterKeyId,
        lastServerKeyId = game_player.lastServerKeyId,
        lastServerPlayerKeyId = game_player.lastServerPlayerKeyId,

        homeServerClusterKeyId = game_player.homeServerClusterKeyId,
        homeServerKeyId = game_player.homeServerKeyId,
        homeServerPlayerKeyId =game_player.homeServerPlayerKeyId,
    )

    return snapshot
