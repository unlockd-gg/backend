import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GroupUsers(ndb.Model):
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()
    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty()
    #playerAvatarTheme = ndb.StringProperty()

    # Firebase auth
    firebaseUser = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)

    update_group_settings = ndb.BooleanProperty()
    update_group_roles = ndb.BooleanProperty()
    update_player_roles = ndb.BooleanProperty()
    ## TODO add more group permissions

    create_events = ndb.BooleanProperty()
    update_events = ndb.BooleanProperty()

    update_games = ndb.BooleanProperty()
    update_servers = ndb.BooleanProperty()

    create_matches = ndb.BooleanProperty()
    create_tournaments = ndb.BooleanProperty()

    applicant = ndb.BooleanProperty()
    approved = ndb.BooleanProperty()
    approved_by = ndb.StringProperty()
    approved_by_userKeyId = ndb.IntegerProperty()
    online = ndb.BooleanProperty()

    order = ndb.IntegerProperty()

    role_title = ndb.StringProperty()
    roleKeyId = ndb.IntegerProperty()

    ## moved to group game users
    #vettingEnabled = ndb.BooleanProperty()
    #vettingCompleted = ndb.BooleanProperty()
    #vettingFinalized = ndb.BooleanProperty()

    #gkpAmount = ndb.FloatProperty()
    #gkpVettingRemaining = ndb.IntegerProperty()

    application_message = ndb.StringProperty()

    def to_json(self):
        return ({
                u'key_id': str(self.key.id()),
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                u'role_title': self.role_title,
                u'order': self.order,
                u'roleKeyId': self.roleKeyId,
                u'picture':self.picture
        })

    def to_json_with_roles(self):
        return ({
                u'key_id': str(self.key.id()),
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                u'role_title': self.role_title,
                u'roleKeyId': self.roleKeyId,
                u'update_group_settings': self.update_group_settings,
                u'update_group_roles': self.update_group_roles,
                u'update_player_roles': self.update_player_roles,
                u'create_events': self.create_events,
                u'update_events': self.update_events,
                u'update_games': self.update_games,
                u'update_servers': self.update_servers,
                u'create_matches': self.create_matches,
                #u'group_member_role': self.group_member_role,
                u'applicant': self.applicant,
                u'approved': self.approved,
                u'picture':self.picture
        })

class GroupUserResponse(messages.Message):
    """ a groups's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    userKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)
    userTitle = messages.StringField(3)
    role_title = messages.StringField(4)
    update_group_settings = messages.BooleanField(5)
    update_group_roles = messages.BooleanField(6)
    update_player_roles = messages.BooleanField(7)
    create_events = messages.BooleanField(8)
    update_events = messages.BooleanField(9)
    update_games = messages.BooleanField(10)
    update_servers = messages.BooleanField(11)
    create_matches = messages.BooleanField(12)
    create_tournaments = messages.BooleanField(13)
    sponsor_tournaments  = messages.BooleanField(14)
    create_ads  = messages.BooleanField(15)
    edit_ads  = messages.BooleanField(16)
    view_transactions  = messages.BooleanField(17)
    chat_membership = messages.BooleanField(18)
    applicant = messages.BooleanField(43)
    approved = messages.BooleanField(44)

    #message = messages.StringField(15)
    #member = messages.BooleanField(16) ## what's this for?
    roleKeyId = messages.IntegerField(30, variant=messages.Variant.INT32)
    order = messages.IntegerField(31, variant=messages.Variant.INT32)
    #playerAvatarTheme = messages.StringField(19)

    groupKeyId = messages.IntegerField(41, variant=messages.Variant.INT32)
    groupTitle = messages.StringField(42)

    application_message = messages.StringField(45)

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)

class GroupUserRequest(messages.Message):
    """ a group members's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    approved = messages.BooleanField(2)
    roleKeyId = messages.IntegerField(3, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    userTitle = messages.StringField(10)
    order = messages.IntegerField(31, variant=messages.Variant.INT32)
    filterby = messages.StringField(32)

GROUP_USER_RESOURCE = endpoints.ResourceContainer(
    GroupUserRequest
)

class GroupUserCollection(messages.Message):
    """ multiple group users """
    group_users = messages.MessageField(GroupUserResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)
