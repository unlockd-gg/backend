import jwt
import datetime
import random
import string
from factory.validation import Validator
from factory.database import Database

from ..settings import *

class Games(object):
    def __init__(self):
        self.validator = Validator()
        self.db = Database()

        self.collection_name = 'games'  # collection name

        self.fields = {
            "title": "string",
            "developer_id": "string",
            "description": "string",
            "instructions": "string",
            "genre": "string",
            "website_url": "string",
            "icon_url": "string",
            "banner_url": "string",
            "party_size_max": "int",
            "supported": "bool",
            "invisible": "bool",
            "invisible_developer": "bool",
            "users_can_create_servers": "bool",
            "groups_can_create_servers": "bool",
            "deploy_matchmaker_servers": "bool",
            "deploy_continuous_servers": "bool",
            "tournaments_supported": "bool",
            "vendors_supported": "bool",
            "api_key": "string",
            "api_secret": "string",
            # TODO - match VM deployment.  Move this out to a different model, so we can support different providers: AWS, Google, etc...
            "metagame_supported": "bool",
            "metagame_url": "string", 
            "matchmaker_local_testing": "bool",
            "matchmaker_local_testing_connection_string": "string",
            "matchmaker_local_testing_api_key": "string",
            "matchmaker_local_testing_api_secret": "string",
            "match_timeout_max_minutes": "int",
            "order": "int",
            "downloadable": "bool",
            "download_url": "string",
            "characters_supported": "bool",
            "character_slot_default": "int",
            # TODO - discord webhooks
            "enforce_locks": "bool",
            "patcher_supported": "bool",
            "patcher_details_xml": "string",
            "patcher_patching": "bool",
            "patcher_prepatch_xml": "string",
            "patcher_server_shutdown_seconds": "int",
            "patcher_server_shutdown_warning_chat": "string",
            "patcher_server_disk_image": "string"


        }

        self.create_required_fields = ["developer_id", "title"]

        # Fields optional for CREATE
        self.create_optional_fields = []

        # Fields required for UPDATE
        self.update_required_fields = []

        # Fields optional for UPDATE
        self.update_optional_fields = ["title", 
                                       ]

    def create(self, game):
        # Validator will throw error if invalid
        self.validator.validate(game, self.fields, self.create_required_fields, self.create_optional_fields)
        res = self.db.insert(game, self.collection_name)
        return res
    
    def create_unique_api_key(self):
        rebuild = True
        while rebuild:
            token1 = self.key_generator(size=6)
            token2 = self.key_generator(size=6)
            token3 = self.key_generator(size=6)
            token4 = self.key_generator(size=6)
            key = token1 + "-" + token2 + "-" + token3 + "-" + token4
            if self.find_by_api_key(key) == None:
                rebuild = False
        return key
    
    def key_generator(self, size=30, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        """ utility method to create keys """
        return ''.join(random.choice(chars) for x in range(size))
    
    def find_by_api_key(self, api_key):
        """ get a game by it's api key """
        found = self.db.find_one({'api_key': api_key}, self.collection_name)
        return found

    def find(self, game):  # find all
        return self.db.find(game, self.collection_name)

    def find_by_id(self, id):
        return self.db.find_by_id(id, self.collection_name)
    
    def find_by_developer_id(self, developer_id):
        found = self.db.find({"developer_id": developer_id}, self.collection_name)
        #if found is None:
        #    return not found
        #if "_id" in found:
        #     found["_id"] = str(found["_id"])
        return found

    def update(self, id, game):
        self.validator.validate(game, self.fields, self.update_required_fields, self.update_optional_fields)
        return self.db.update(id, game,self.collection_name)

    def delete(self, id):
        return self.db.delete(id, self.collection_name)
    
    
    def to_json(self, thisgame):
        if 'title' in thisgame.keys():
            title = thisgame['title']
        else:
            title = ""


        return_data = {
            "title": title,
        }
        return return_data
    

