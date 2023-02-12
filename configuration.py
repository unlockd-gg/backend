import datetime

# Get this from the console.cloud.google.com API access section.
# Ends in .apps.googleusercontent.com
WEB_CLIENT_ID = ''
# Get this from the console.cloud.google.com API access section.
# Ends in .apps.googleusercontent.com
WEB_CLIENT_AUTOCREATED_BY_GOOGLE = ''

## these web client identifiers are also in the following files:
## /static/app/js/416_tokenapp.js
## /static/app/js/app.js
## /static/app/js/tokenapp.js

# Get this from the console.cloud.google.com API access section.
GOOGLE_SERVER_API_KEY = ''


# Link to your socketserver
HEROKU_SOCKETIO_SERVER = ""

# Twitch API credentials
TWITCH_CLIENT_ID = ""
TWITCH_CLIENT_SECRET = ""

#openexchangerates.org
OPENEXCHANGERATES_APPID = ""

# Braintree SANDBOX
#BRAINTREE_MERCHANT_ID="",
#BRAINTREE_PUBLIC_KEY="",
#BRAINTREE_PRIVATE_KEY=""

# Braintree LIVE
BRAINTREE_MERCHANT_ID=""
BRAINTREE_PUBLIC_KEY=""
BRAINTREE_PRIVATE_KEY=""

# Global admin discord webhooks.  Create these on your admin discord channel within discord.
DISCORD_WEBHOOK_ADMIN = ""
DISCORD_WEBHOOK_PAYMENTS = ""

RESTRICTED_ENDPOINTS_ALLOWED_ORIGINS = ["https://ue4topia.appspot.com", "https://uetopia.com", "https://www.uetopia.com", "http://localhost:8080", "https://apitest-dot-ue4topia.appspot.com"]

## Heads up!
## configure mailjet inside of app.yaml
## configure firebase inside of /static/app/index.html

# unused deprecate
SERVER_CREATE_DEFAULT_MINIMUMCURRENCYHOLD = 1000000
SERVER_CREATE_DEFAULT_INCREMENTCURRENCY = 100000
AUTO_AUTH_THRESHOLD_MAXIMUM = 10000000
AUTO_AUTH_MINIMUM_HOLD_MULTIPLIER = 10

## continuous server allocation
CONTINUOUS_SERVER_WAIT_FOR_DONE_INITIAL_DELAY_SECONDS = 20
CONTINUOUS_SERVER_WAIT_FOR_DONE_DELAY_SECONDS = 5
CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS = 300
CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_RANDOMIZE_SECONDS = 300
CONTINUOUS_SERVER_WAIT_FOR_DEALLOCATE_UNUSED_SECONDS = 1800

## auto expire time for players that are stuck in active state.
ACTIVE_SERVER_PLAYER_MEMBER_AUTO_EXPIRE_TIME = datetime.timedelta(minutes=1440) #24 hours
MATCH_PLAYER_AUTO_EXPIRE_TIME = datetime.timedelta(minutes=180)

VM_INSTANCE_MINIMUM_SECONDS = 660

SERVER_TRANSACTION_QUEUE_MINIMUM_INTERVAL = datetime.timedelta(seconds=5)
## Be sure to also set the min_backoff_seconds in queue.yaml to match!

SERVER_DEAUTHORIZE_TIMEOUT_SECONDS = 65


## material icons
MATERIAL_ICON_AUTO_AUTH_FAILURE = "warning"
MATERIAL_ICON_NEW_USER_PAYMENT = "credit_card"
MATERIAL_ICON_VM_CREATE = "room_service"
MATERIAL_ICON_ADMISSION_FEE = "event_seat"
MATERIAL_ICON_SERVER_DEAUTHORIZE = "turned_in_not"
MATERIAL_ICON_SERVER_AUTHORIZE = "turned_in"
MATERIAL_ICON_DONATE = "loyalty"
MATERIAL_ICON_REWARD = "stars"
MATERIAL_ICON_PURCHASE = "shopping_cart"
MATERIAL_ICON_TRANSFER = "input"
MATERIAL_ICON_SERVER_BILL = "receipt"
MATERIAL_ICON_FRIENDS = "favorite"
MATERIAL_ICON_REFERRAL = "supervisor_account"
MATERIAL_ICON_GAME = "games"
MATERIAL_ICON_MATCH_WIN = "star"
MATERIAL_ICON_SERVER_CREATE= "build"
MATERIAL_ICON_SERVER_TO_GAME_TRANSFER = "toll"
MATERIAL_ICON_TIP = "thumb_up"
MATERIAL_ICON_GROUP = "group"
MATERIAL_ICON_TOURNAMENT = "transform"
MATERIAL_ICON_VENDOR= "local_grocery_store"
MATERIAL_ICON_DELETE= "delete"
MATERIAL_ICON_MATCH_PLAYER_EXPIRED = "slow_motion_video"
MATERIAL_ICON_AGREEMENT = "update"
MATERIAL_ICON_CRED_PURCHASE = "input"
MATERIAL_ICON_AD_REJECTED = "thumb_down"
MATERIAL_ICON_AD_SHOWN = "airplay"
MATERIAL_ICON_AD_REFUND = "keyboard_return"
MATERIAL_ICON_VOUCHER_REDEEM = "verified_user"

## Server Instance price calculations
## Thse are calculated on the fly now - deprecate
SERVER_HOURLY_RATE_USD = 0.047
SERVER_MINUTE_RATE_USD = SERVER_HOURLY_RATE_USD / 60.0
CRED_TO_USD_CONVERSION = 0.00006573 # https://99bitcoins.com/satoshi-usd-converter/  USD > Satoshi
USD_TO_CRED_CONVERSION = 65 # Enter .01 in the usd to satoshi box

#SERVER_MINUTE_RATE_CRED = SERVER_MINUTE_RATE_USD / CRED_TO_USD_CONVERSION

##  113187 = 1 / 0.0000088349
## example, $1.00 USD = 113,029 CRED

## FREE MONEY
CRED_BONUS_NEW_USER_ACCOUNT_CREATION = 5000
CRED_BONUS_REFERRAL = 2500
BONUS_REFERRALS_ENABLED = False

## MATCHMAKER
MATCHMAKER_RANK_MARGIN = 1000 # how much margin is permitted for matchmaker
MATCHMAKER_QUEUE_PROCESS_MAXIMUM_CONSECUTIVE_FAILURES = 4
MATCHMAKER_QUEUE_PROCESS_REQUEUE_EMPTY_SECONDS = 60
MATCHMAKER_QUEUE_PROCESS_REQUEUE_LEFTOVER_SECONDS = 30
MATCHMAKER_QUEUE_PROCESS_REQUEUE_MORE_SECONDS = 2
MATCHMAKER_MAXIMUM_VERIFICATION_GRACE_PERIOD = datetime.timedelta(hours=6)
MATCHMAKER_WAIT_FOR_DEALLOCATE_DELAY_SECONDS = 60
MATCHMAKER_WAIT_FOR_DEALLOCATE_UNUSED_SECONDS = 600
MATCHMAKER_WAIT_FOR_LOCAL_KEY_SECRET_CLEAR_DELAY_SECONDS = 45


## GROUPS
GROUP_TAG_MINIMUM_STR_SIZE = 1
GROUP_TAG_MAXIMUM_STR_SIZE = 9

## tournaments
TOURNAMENT_MAXIMUM_TEAMS = 8
TOURNAMENT_SIGNUP_DURATION_DEFAULT = datetime.timedelta(minutes=10)
TOURNAMENT_SIGNUP_TO_PLAY_TRANSITION_DEFAULT = datetime.timedelta(minutes=1)
TOURNAMENT_PLAY_DURATION_DEFAULT = datetime.timedelta(minutes=120)
TOURNAMENT_TIMEOUT_NOT_COMPLETED = datetime.timedelta(minutes=10)

## TEAMS
TEAM_MAXIMUM_SIZE = 16

## Vendors
VENDOR_OFFER_AUTO_EXPIRE_TIME = datetime.timedelta(days=14)

PROFILE_UPDATE_INTERVAL_MINIMUM_SECONDS = 1



UETOPIA_GROSS_PERCENTAGE_RAKE = 0.05

SERVER_CLUSTER_MANAGER_PLACEHOLDER_STALE_TIME = datetime.timedelta(seconds=120)
