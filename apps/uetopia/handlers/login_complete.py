import logging
from apps.handlers import BaseHandler
from google.appengine.api import users
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.user_login_tokens import UserLoginTokensController

class IndexHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def get(self):
        """ Static Index

        """
        user = users.get_current_user()
        usersController = UsersController()
        ultController = UserLoginTokensController()

        userrecord = usersController.get_by_googleUser(str(user))

        user_login_token = ultController.get_by_userKeyId(userrecord.key.id())

        access_token = ultController.create_unique_access_token()
        custom_title = self.request.get('redirect_uri') + "&access_token=" + access_token

        if not user_login_token:
            user_login_token = ultController.create(
            userKeyId = userrecord.key.id(),
            access_token = access_token
            )
            return self.render_html_response(
                    "error.html",
                    title=custom_title,
                    message = "you are logged in"
                    )
        else:
            ## update existing

            user_login_token.access_token = access_token
            ultController.update(user_login_token)

            return self.render_html_response(
                    "error.html",
                    title=custom_title,
                    message = "you are logged in"
                    )
