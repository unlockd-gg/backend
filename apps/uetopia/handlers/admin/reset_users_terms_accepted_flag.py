import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from google.appengine.datastore.datastore_query import Cursor
from apps.uetopia.controllers.users import UsersController
from configuration import *

class ResetUserTermsAcceptedFlagHandler(BaseHandler):
    def post(self):
        logging.info('ResetUserTermsAcceptedFlagHandler')

        userController = UsersController()

        if self.request.get('cursor'):
            curs = Cursor(urlsafe=self.request.get('cursor'))
        else:
            curs = Cursor()

        #users_with_terms_accepted, cursor, more = userController.list_by_terms_accepted()
        all_users, cursor, more  = userController.list_page(start_cursor=curs)

        for thisuser in all_users:
            logging.info('processing user')
            if thisuser.agreed_with_terms:
                thisuser.agreed_with_terms = False
                thisuser.profile_saved = False
                thisuser.developer = False
                userController.update(thisuser)

                ## push an alert out to firebase
                description = "Our EULA and DLA have been updated.  Developer flags have been reset.  Visit your profile to re-enable"
                taskUrl='/task/user/alert/create'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': thisuser.firebaseUser,
                                                                                'material_icon': MATERIAL_ICON_AGREEMENT,
                                                                                'importance': 'md-primary',
                                                                                ## TODO this message can be more helpful
                                                                                'message_text': description,
                                                                                'action_button_color': 'primary',
                                                                                'action_button_sref': '#/profile'
                                                                                })

        if more:
            logging.info('Found more.  Re-queue the task.')

            if cursor:
                cursor_urlsafe = cursor.urlsafe()
            else:
                cursor_urlsafe = None

            taskUrl='/admin/user/reset_terms_accepted_flag'
            taskqueue.add(url=taskUrl, queue_name='userResetTermsAccepted', params={ 'cursor': cursor_urlsafe })

        return self.render_json_response(
            users_processed = len(all_users),
            #more = more
        )
    def get(self):
        logging.info('ResetUserTermsAcceptedFlagHandler')

        userController = UsersController()

        if self.request.get('cursor'):
            curs = Cursor(urlsafe=self.request.get('cursor'))
        else:
            curs = Cursor()

        #users_with_terms_accepted, cursor, more = userController.list_by_terms_accepted()
        all_users, cursor, more  = userController.list_page(start_cursor=curs)

        for thisuser in all_users:
            logging.info('processing user')
            if thisuser.agreed_with_terms:
                thisuser.agreed_with_terms = False
                thisuser.profile_saved = False
                thisuser.developer = False
                userController.update(thisuser)

                ## push an alert out to firebase
                description = "Our EULA and DLA have been updated.  Developer flags have been reset.  Visit your profile to re-enable"
                taskUrl='/task/user/alert/create'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': thisuser.firebaseUser,
                                                                                'material_icon': MATERIAL_ICON_AGREEMENT,
                                                                                'importance': 'md-primary',
                                                                                ## TODO this message can be more helpful
                                                                                'message_text': description,
                                                                                'action_button_color': 'primary',
                                                                                'action_button_sref': '#/profile'
                                                                                })

        if more:
            logging.info('Found more.  Re-queue the task.')

            if cursor:
                cursor_urlsafe = cursor.urlsafe()
            else:
                cursor_urlsafe = None

            taskUrl='/admin/user/reset_terms_accepted_flag'
            taskqueue.add(url=taskUrl, queue_name='userResetTermsAccepted', params={ 'cursor': cursor_urlsafe })

        return self.render_json_response(
            users_processed = len(all_users),
            #more = more
        )
