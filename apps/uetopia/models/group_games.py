import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class GroupGames(ndb.Model):
    """ a connection between a group and a game

    """
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()
    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty()

    discordWebhook = ndb.StringProperty()
    discord_subscribe_game_event_feeds = ndb.BooleanProperty(indexed=False)
    discord_subscribe_game_event_feed_kills = ndb.BooleanProperty(indexed=False)
    discord_subscribe_game_event_feed_wins = ndb.BooleanProperty(indexed=False)
    discord_subscribe_game_ad_status_changes = ndb.BooleanProperty(indexed=False)

    show_game_on_group_page = ndb.BooleanProperty(indexed=False)
    inGameTextureServingUrl = ndb.StringProperty()  ## this is specific to the game.  it can be a single texture ot a link to a folder full of images.

    def to_json(self):
        return ({
            u'key_id': str(self.key.id()),
            u'groupKeyId': self.groupKeyId,
            u'gameKeyId': self.gameKeyId,
            u'gameTitle': self.gameTitle,
            u'show_game_on_group_page': self.show_game_on_group_page
        })

class GroupGameGetRequest(messages.Message):
    """ a Group's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    show_game_on_group_page = messages.BooleanField(24)

GROUP_GAME_CONNECT_RESOURCE = endpoints.ResourceContainer(
    GroupGameGetRequest
)

class GroupGameResponse(messages.Message):
    """ a Group Game's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    gameKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    gameTitle = messages.StringField(3)
    groupKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    groupTitle = messages.StringField(5)
    discordWebhook = messages.StringField(6)
    discord_subscribe_game_event_feeds = messages.BooleanField(21)
    discord_subscribe_game_event_feed_kills = messages.BooleanField(22)
    discord_subscribe_game_event_feed_wins = messages.BooleanField(23)
    discord_subscribe_game_ad_status_changes = messages.BooleanField(24)

    show_game_on_group_page = messages.BooleanField(34)
    inGameTextureServingUrl = messages.StringField(35)

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)

GROUP_GAME_EDIT_RESOURCE = endpoints.ResourceContainer(
    GroupGameResponse
)
