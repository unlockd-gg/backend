import logging
import datetime
import json
import os
import mailjet_rest
import requests_toolbelt.adapters.appengine
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.datastore.datastore_query import Cursor
from apps.uetopia.controllers.users import UsersController
from configuration import *


# Use the App Engine requests adapter to allow the requests library to be
# used on App Engine.
requests_toolbelt.adapters.appengine.monkeypatch()

MAILJET_API_KEY = os.environ['MAILJET_API_KEY']
MAILJET_API_SECRET = os.environ['MAILJET_API_SECRET']
MAILJET_SENDER = os.environ['MAILJET_SENDER']

class BatchUpdateMailjetHandler(BaseHandler):
    def post(self):
        logging.info('BatchUpdateMailjetHandler')

        userController = UsersController()

        if self.request.get('cursor'):
            curs = Cursor(urlsafe=self.request.get('cursor'))
        else:
            curs = Cursor()

        #users_with_terms_accepted, cursor, more = userController.list_by_terms_accepted()
        all_users, cursor, more  = userController.list_page(start_cursor=curs)

        contacts_temp = []

        for thisuser in all_users:
            logging.info('processing user')
            ## check if promotions is enabled?
            ## just doing all users list for now
            contact_temp = {
                    "Email": thisuser.email,
                    "Name": thisuser.title,
            }
            contacts_temp.append(contact_temp)



        ## set up the request
        client = mailjet_rest.Client(
        auth=(MAILJET_API_KEY, MAILJET_API_SECRET))

        data = {
              'ContactsLists': [
                            {
                                    "ListID": 184,
                                    "action": "addforce"
                            }
                    ],
              'Contacts': contacts_temp
            }

        logging.info(data)

        result = client.contact_managemanycontacts.create(data=data)
        logging.info(result.status_code)

        logging.info(result.json())


        if more:
            logging.info('Found more.  Re-queue the task.')

            if cursor:
                cursor_urlsafe = cursor.urlsafe()
            else:
                cursor_urlsafe = None

            taskUrl='/admin/user/batch_update_mailjet'
            taskqueue.add(url=taskUrl, queue_name='userResetTermsAccepted', params={ 'cursor': cursor_urlsafe })

        return self.render_json_response(
            users_processed = len(all_users),
            #more = more
        )
    def get(self):
        logging.info('BatchUpdateMailjetHandler')

        return self.post()
