import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GroupRoles(ndb.Model):
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()
    title = ndb.StringProperty()
    description = ndb.StringProperty()

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
    sponsor_tournaments = ndb.BooleanProperty()

    create_ads = ndb.BooleanProperty()
    edit_ads = ndb.BooleanProperty()
    view_transactions = ndb.BooleanProperty()

    chat_membership = ndb.BooleanProperty()

    applicant_role = ndb.BooleanProperty()
    leader_role = ndb.BooleanProperty()

    order = ndb.IntegerProperty()

    join_group_servers = ndb.BooleanProperty()
    join_group_server_instances = ndb.BooleanProperty()
    join_group_tournaments = ndb.BooleanProperty()

    drop_items_in_group_servers = ndb.BooleanProperty()
    pickup_items_in_group_servers = ndb.BooleanProperty()

    donate_to_members = ndb.BooleanProperty()

    metagame_faction_lead = ndb.BooleanProperty()
    metagame_team_lead = ndb.BooleanProperty()

    raid_lead = ndb.BooleanProperty()


    def to_json(self):
        return ({
                u'key_id': self.key.id(),
                u'groupKeyId': self.groupKeyId,
                u'title': self.title,
                u'description': self.description,
                u'update_group_settings': self.update_group_settings,
                u'update_group_roles': self.update_group_roles,
                u'update_player_roles': self.update_player_roles,
                u'create_events': self.create_events,
                u'update_events': self.update_events,
                u'update_games': self.update_games,
                u'update_servers': self.update_servers,
                u'create_matches': self.create_matches,
                u'create_tournaments': self.create_tournaments,
                u'sponsor_tournaments': self.sponsor_tournaments,

                u'create_ads' : self.create_ads,
                u'edit_ads' :self.edit_ads,
                u'view_transactions' : self.view_transactions,

                u'chat_membership': self.chat_membership,
                u'applicant_role': self.applicant_role,
                u'leader_role': self.leader_role,
                u'order': self.order,
                u'join_group_servers': self.join_group_servers,
                u'join_group_server_instances': self.join_group_server_instances,
                u'join_group_tournaments': self.join_group_tournaments,
                u'drop_items_in_group_servers': self.drop_items_in_group_servers,
                u'pickup_items_in_group_servers': self.pickup_items_in_group_servers,
                u'donate_to_members': self.donate_group_to_users,
                u'metagame_faction_lead': self.metagame_faction_lead,
                u'metagame_team_lead': self.metagame_team_lead,
                u'raid_lead': self.raid_lead
        })

### PROTORPC MODELS FOR ENDPOINTS

class GroupRolesGetRequest(messages.Message):
    """ a Group Roles's key """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(45, variant=messages.Variant.INT32)

GROUP_ROLES_GET_RESOURCE = endpoints.ResourceContainer(
    GroupRolesGetRequest
)

class GroupRoleResponse(messages.Message):
    """ a group roles's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    update_group_settings = messages.BooleanField(4)
    update_group_roles = messages.BooleanField(5)
    update_player_roles = messages.BooleanField(6)
    create_events = messages.BooleanField(7)
    update_events = messages.BooleanField(8)
    update_games = messages.BooleanField(9)
    update_servers = messages.BooleanField(10)
    create_matches = messages.BooleanField(11)
    create_tournaments = messages.BooleanField(12)
    sponsor_tournaments = messages.BooleanField(13)
    create_ads = messages.BooleanField(14)
    edit_ads = messages.BooleanField(15)
    view_transactions = messages.BooleanField(16)
    chat_membership = messages.BooleanField(31)
    applicant_role = messages.BooleanField(42)
    leader_role = messages.BooleanField(43)
    order = messages.IntegerField(44, variant=messages.Variant.INT32)
    groupKeyId = messages.IntegerField(45, variant=messages.Variant.INT32)
    join_group_servers = messages.BooleanField(51)
    join_group_server_instances = messages.BooleanField(52)
    join_group_tournaments = messages.BooleanField(53)
    drop_items_in_group_servers = messages.BooleanField(54)
    pickup_items_in_group_servers = messages.BooleanField(55)
    donate_to_members = messages.BooleanField(56)
    metagame_faction_lead = messages.BooleanField(57)
    metagame_team_lead = messages.BooleanField(58)
    raid_lead = messages.BooleanField(59)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)

GROUP_ROLES_RESOURCE = endpoints.ResourceContainer(
    GroupRoleResponse
)



class GroupRoleCreateRequest(messages.Message):
    """ a group events's data """
    groupKeyId = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    update_group_settings = messages.BooleanField(4)
    update_group_roles = messages.BooleanField(5)
    update_player_roles = messages.BooleanField(6)
    create_events = messages.BooleanField(7)
    update_events = messages.BooleanField(8)
    update_games = messages.BooleanField(9)
    update_servers = messages.BooleanField(10)
    create_matches = messages.BooleanField(11)
    create_tournaments = messages.BooleanField(12)
    sponsor_tournaments = messages.BooleanField(13)
    create_ads = messages.BooleanField(14)
    edit_ads = messages.BooleanField(15)
    view_transactions = messages.BooleanField(16)
    chat_membership = messages.BooleanField(31)
    applicant_role = messages.BooleanField(42)
    leader_role = messages.BooleanField(43)
    order = messages.IntegerField(44, variant=messages.Variant.INT32)
    join_group_servers = messages.BooleanField(51)
    join_group_server_instances = messages.BooleanField(52)
    join_group_tournaments = messages.BooleanField(53)
    drop_items_in_group_servers = messages.BooleanField(54)
    pickup_items_in_group_servers = messages.BooleanField(55)
    donate_to_members = messages.BooleanField(56)
    metagame_faction_lead = messages.BooleanField(57)
    metagame_team_lead = messages.BooleanField(58)
    raid_lead = messages.BooleanField(59)

GROUP_ROLE_CREATE_RESOURCE = endpoints.ResourceContainer(
    GroupRoleCreateRequest
)

class GroupRoleCollection(messages.Message):
    """ multiple roles """
    roles = messages.MessageField(GroupRoleResponse, 1, repeated=True)
    key_id = messages.IntegerField(3, variant=messages.Variant.INT32)
    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)


GROUP_ROLE_COLLECTION = endpoints.ResourceContainer(
    GroupRoleCollection
)
