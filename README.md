unlockd backend
======================

Multiplayer game backend.

features: Abilities, Inventory, Action bar, Chat, Characters, Friends, Recent Players, Party, Guilds/Clans, Player owned vendors, Game Store (microtransactions), Matchmaker, Tournaments, External Metagame, Leaderboard, Server persistence, Player data persistence, Server connections (travel), Server instances (private, guild, party), Server management, Server List, Access Control, Sponsors / Ads, Consignments, Player Statistics, Achievements.

## Main Branch

This branch is in active development.  We are working on rewriting the backend logic for modern docker based architecture.  The old python2 appengine architecture has been moved to the "python2-appengine-deprecated" branch.  

## DISCLAIMER

This is pre-beta code, and comes with no support, or assurances.  See the license for details.

## Live Version

Previous version is running here:

https://uetopia.com

## Directory Layout

- TBD - in active development

## Installation notes

- lightning login requires a network accessible ip address for some provicers (getalby), and an https accessbile domain name for others (WoS).  

## Local/Dev Installation 

- install docker desktop
- docker compose up

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
- docker compose up --build


# Build the angular files.
ng build --configuration development