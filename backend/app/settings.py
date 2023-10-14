import os

## Secret key for JWT auth
## TODO set this to something unique
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '') 
MAILJET_API_KEY = os.getenv('MAILJET_API_KEY', '') 
MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY', '') 
MAILJET_SENDER = os.getenv('MAILJET_SENDER', '') 

GETALBY_WEBHOOKID = os.getenv('GETALBY_WEBHOOKID', '')
GETALBY_WEBHOOK_SECRET = os.getenv('GETALBY_WEBHOOK_SECRET', '')
GETALBY_INVOICE_TOKEN = os.getenv('GETALBY_INVOICE_TOKEN', '')