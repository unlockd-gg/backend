unlockd backend
======================

Multiplayer game backend.

features: Abilities, Inventory, Action bar, Chat, Characters, Friends, Recent Players, Party, Guilds/Clans, Player owned vendors, Game Store (microtransactions), Matchmaker, Tournaments, External Metagame, Leaderboard, Server persistence, Player data persistence, Server connections (travel), Server instances (private, guild, party), Server management, Server List, Access Control, Sponsors / Ads, Consignments, Player Statistics, Achievements.

## DISCLAIMER

This is pre-beta code, and comes with no support, or assurances.  See the license for details.

## Live Version

Previous version is running here:

https://uetopia.com

## Directory Layout

- lib/: Python library files not included in the standard runtime environment.
- model/: Python NDB class definitions. NDB is the schemaless object datastore
  on the App Engine.
- service/: Python Cloud Endpoints definitions. Defines the API backend classes.
- static/: Client side HTML, JavaScript, and other static files. The files in
  this folder are similar in layout to the Angular Seed application.
- app.yaml: App Engine configuration file. Defines paths and Python handlers.
- fix_path.py: Python file to set up our standard project include path.
- services.py: Python handler for the Cloud Endpoints. Choose which API service
  classes are active.

## Installation

- Install the socketserver at heroku or on another nodeJS provider.
- sign up for an account with OpenExchangeRates if you want real time exchange rates

- pip install -t lib requirements.txt
- edit configuration.py adding all api keys and webhooks
- install google cloud
- Create a new google cloud project.
  enable billing
  enable datastore
  enable cloud tasks
  enable firebase (in realtime mode)
  enable compute engine
- find and replace for ue4topia.appspot.com to replace with your project.
- deploy the project.
gcloud app deploy --project [your project] app.yaml queue.yaml index.yaml cron.yaml -v 1 --promote

- login to the project via the link that the deploy command provided (yourproject.appspot.com)
- after successful login, go to the console.cloud.google.com datastore viewer and edit your user database entry
  set admin to true.  Save.
- Close the browser and relaunch it, navigate back to the site.
- You should see admin now in the nav after a few seconds.
- click your name and select profile > Show optional fields > select developer.  Save.
- After a few seconds you should see developer in the nav
