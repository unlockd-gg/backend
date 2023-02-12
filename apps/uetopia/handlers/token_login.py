import logging
from apps.handlers import BaseHandler
from google.appengine.api import users
from apps.uetopia.controllers.users import UsersController

class IndexHandler(BaseHandler):
    """
    Send out a static Index page

    """
    def get(self):
        """ Static Index

        """
        user = users.get_current_user()
        usersController = UsersController()

        authorized_user = usersController.get_by_googleUser(str(user))

        if not authorized_user:
            return self.render_html_response(
                "error.html",
                message = "could not find your user account. log in the regular way.."
                )


        redirect_uri = '/login_complete.html?access_token=test123&redirect_uri=' + self.request.get('redirect_uri')

        return self.redirect(redirect_uri)
