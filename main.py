#!/usr/bin/env python

import endpoints
import webapp2
from webapp2 import Route

#from api_collection import api_collection
from service import users
from service import games
from service import servers
from service import transactions
from service import user_relationships
from service import groups
from service import teams
from service import chat
from service import tournaments
from service import vendors
from service import characters
from service import ads


#app = endpoints.api_server(api_collection)


# Set the secret key for the session cookie
config = {
    'webapp2_extras.sessions': {
        'secret_key': 'SOMETHING_UNIQUE'
    }
}

routes = [
]

# URLS
from apps.uetopia.urls import routes as uetopia_routes
routes.extend(uetopia_routes)

from apps.uetopia.api.urls import routes as api_routes
routes.extend(api_routes)

from apps.uetopia.handlers.tasks.urls import routes as task_routes
routes.extend(task_routes)

from apps.uetopia.handlers.cron.urls import routes as cron_routes
routes.extend(cron_routes)

from apps.uetopia.handlers.patcher.urls import routes as patcher_routes
routes.extend(patcher_routes)

from apps.uetopia.handlers.admin.urls import routes as admin_routes
routes.extend(admin_routes)

app = webapp2.WSGIApplication(
    routes,
    debug=True,
    config=config
)



def main():
    app.run()

if __name__ == '__main__':
    main()
