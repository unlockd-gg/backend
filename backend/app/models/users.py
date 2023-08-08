import jwt
import datetime
from factory.validation import Validator
from factory.database import Database

from ..settings import *

class Users(object):
    def __init__(self):
        self.validator = Validator()
        self.db = Database()

        self.collection_name = 'users'  # collection name

        self.fields = {
            "title": "string",
            "emailaddress": "string",
            "admin": "bool",
            "currencyBalance": "int",
            "developer": "bool",
            "groupTag": "string",
            "groupId": "string",
            "defaultTeamTitle": "string",
            "region": "string",
            "referral_processed": "bool",
            "referred_by": "string",
            "twitch_streamer": "bool",
            "twitch_channel_id": "string",
            "twitch_currently_streaming": "bool",
            "twitch_stream_game": "string",
            "twitch_stream_viewers": "int",
            "created": "datetime",
            "updated": "datetime",
        }

        self.create_required_fields = ["emailaddress"]

        # Fields optional for CREATE
        self.create_optional_fields = []

        # Fields required for UPDATE
        self.update_required_fields = []

        # Fields optional for UPDATE
        self.update_optional_fields = ["title", 
                                       "admin", 
                                       "emailaddress", 
                                       "developer", 
                                       "defaultTeamTitle", 
                                       "region",
                                        "referral_processed",
                                        "referred_by",
                                        "twitch_streamer",
                                        "twitch_channel_id",
                                        "twitch_currently_streaming",
                                        "twitch_stream_game",
                                        "twitch_stream_viewers"
                                       ]

    def create(self, user):
        # Validator will throw error if invalid
        self.validator.validate(user, self.fields, self.create_required_fields, self.create_optional_fields)
        res = self.db.insert(user, self.collection_name)
        return res

    def find(self, user):  # find all
        return self.db.find(user, self.collection_name)

    def find_by_id(self, id):
        return self.db.find_by_id(id, self.collection_name)
    
    def find_by_emailaddress(self, emailaddress):
        found = self.db.find_one({"emailaddress": emailaddress}, self.collection_name)
        #if found is None:
        #    return not found
        #if "_id" in found:
        #     found["_id"] = str(found["_id"])
        return found

    def update(self, id, user):
        self.validator.validate(user, self.fields, self.update_required_fields, self.update_optional_fields)
        return self.db.update(id, user,self.collection_name)

    def delete(self, id):
        return self.db.delete(id, self.collection_name)
    
    
    def to_json(self, thisuser):
        if 'title' in thisuser.keys():
            title = thisuser['title']
        else:
            title = ""

        if 'emailaddress' in thisuser.keys():
            emailaddress = thisuser['emailaddress']
        else:
            emailaddress = ""

        if 'admin' in thisuser.keys():
            admin = thisuser['admin']
        else:
            admin = False

        if 'developer' in thisuser.keys():
            developer = thisuser['developer']
        else:
            developer = False

        return_data = {
            "title": title,
            "emailaddress": emailaddress,
            "admin": admin,
            "developer": developer
        }
        return return_data
    

