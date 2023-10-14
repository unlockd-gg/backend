unlockd backend
======================

Multiplayer game backend.

Features working:  None.  We're working on converting these over from the old version.

Features TODO: Abilities, Inventory, Action bar, Chat, Characters, Friends, Recent Players, Party, Guilds/Clans, Player owned vendors, Game Store (microtransactions), Matchmaker, Tournaments, External Metagame, Leaderboard, Server persistence, Player data persistence, Server connections (travel), Server instances (private, guild, party), Server management, Server List, Access Control, Sponsors / Ads, Consignments, Player Statistics, Achievements.

## Main Branch

This branch is in active development.  We are working on rewriting the backend logic for modern docker based architecture.  The old python2 appengine architecture has been moved to the "python2-appengine-deprecated" branch.  

## DISCLAIMER

This is pre-beta code, and comes with no support, or assurances.  See the license for details.

## Live Demo

https://unlockd.gg

## Directory Layout

- backend:  python flask API endpoints
- nginx: container routing
- unlockd-webclient:  Angular 16 frontend

## Installation notes

- lightning login requires a network accessible ip address for some provicers (getalby), and an https accessbile domain name for others (WoS).  
- If you don't have an SSL enabled domain name for development, just use the email login functionality.  You can get the auth code by visiting:  /api/lightning/wallets  (this email login AND THIS API ENDPOINT should not be used in production - for convenience only)

## Lightning payment setup

- Update dockercompose with a unique webhookid
- Create an account on getalby.com
- Create a webhook https://getalby.com/developer/webhook_endpoints
- URL should be: https://yourdomain/api/webhooks/getalby/webhookid (replace domain and webhookid)
- Save the webhook secret, and paste it into dockercompose

## Local/Dev Installation 

- install docker desktop
- clone the repo
- cp docker-compose-template.yml docker-compose.yml
- vi docker-compose.yaml # Add env vars.
- docker compose up
- open a VSCode window to the frontend by itself
- ng serve
- open a VSCode window to the backend by itself
- create python environment using requirements.txt 

## AWS Production Installation

- Create an ec2 instance (ubuntu latest) (suggest adding some extra storage space 8gb will run out)
- Create and assosiate an elastic IP address to this instance for convenience
- Create an ec2 target group
- Create an ec2 load balancer
- SSH into the instance
- mkdir docker
- cd docker
- install docker (https://docs.docker.com/engine/install/ubuntu/) (remember the group/user step)
- git clone https://github.com/unlockd-gg/backend.git 
- cd backend
- cp docker-compose-template.yml docker-compose.yml
- vi docker-compose.yaml # Add env vars.
- update ip address (or SSL domain): webclient/src/app/app.component.ts, login-dialog/login-dialog-component.ts, webclient/src/app/lightning.service.ts, backend/app/views.py (91)
- docker compose up --build


# Making frontend changes
- after changing html, ts, or css, run:
- ng build --configuration development