import endpoints
import logging
import uuid
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

##from apps.uetopia.providers import firebase_helper

from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.user_relationships import UserRelationshipsController
from apps.uetopia.controllers.tournaments import TournamentsController
from apps.uetopia.controllers.teams import TeamsController
from apps.uetopia.controllers.team_members import TeamMembersController

from apps.uetopia.controllers.chat_messages import ChatMessagesController
from apps.uetopia.controllers.chat_channels import ChatChannelsController
from apps.uetopia.controllers.chat_channel_subscribers import ChatChannelSubscribersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class TeamDeleteHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] TeamDeleteHandler")

        teamMembersController = TeamMembersController()
        teamController = TeamsController()

        chatChannelController = ChatChannelsController()
        chatChannelSubscribersController = ChatChannelSubscribersController()
        chat_message_controller = ChatMessagesController()


        ## this is a teamKeyId
        key_id = self.request.get('key_id')
        ## get the team
        team = teamController.get_by_key_id(int(key_id))

        if not team:
            logging.error('team not found')
            return





        team_members = teamMembersController.get_by_teamKeyId(int(key_id))
        if not team_members:
            logging.info('team_members not found')
            #return

        ## No checks are done here.  They should have all been done previously.

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())
        headers = {"Content-Type": "application/json"}

        team.purged = True ## Indicate to UE game clients that we are deleting!
        team.members = []
        team.userIsCaptain = None
        team_json = json.dumps(team.to_json_with_members())

        ## get the team chat channel
        party_chat_channel = chatChannelController.get_by_channel_type_refKeyId("team", team.key.id())


        for team_member in team_members:
            ## First, push down a message that the team was deleted
            # push out to in-game clients via heroku
            # ignore if it's failing
            try:
                URL = "%s/user/%s/team/%s" % (HEROKU_SOCKETIO_SERVER, team_member.userFirebaseUser, team_member.teamKeyId)
                resp, content = http_auth.request(URL,
                                    ##"PATCH",
                                  "PUT", ## Write or replace data to a defined path,
                                  team_json,
                                  headers=headers)

                logging.info(resp)
                logging.info(content)
            except:
                logging.error('heroku error')

            ## delete the chat channel subscriber
            if party_chat_channel:
                subscriber = chatChannelSubscribersController.get_by_channel_and_user(party_chat_channel.key.id(), team_member.userKeyId)
                if subscriber:
                    chatChannelSubscribersController.delete(subscriber)
                    chat_message = "> Left party chat"
                    ## push the chat channel list and a chat message
                    taskUrl='/task/chat/channel/list_changed'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': team_member.userFirebaseUser,
                                                                                    'userKeyId': team_member.userKeyId,
                                                                                    'textMessage': chat_message
                                                                                    }, countdown = 2)

                    taskUrl='/task/chat/send'
                    taskqueue.add(url=taskUrl, queue_name='channelMessaging', params={'firebaseUser': team_member.userFirebaseUser,
                                                                                        "message": chat_message,
                                                                                        "created":datetime.datetime.now().isoformat()
                                                                                    })

            teamMembersController.delete(team_member)

        ## delete the chat channel
        if party_chat_channel:
            chatChannelController.delete(party_chat_channel)

        ## TODO delete from firebase too?
        teamController.delete(team)


        return
