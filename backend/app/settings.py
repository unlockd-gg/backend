import os

## Secret key for JWT auth
## TODO set this to something unique
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '') 
MAILJET_API_KEY = os.getenv('MAILJET_API_KEY', '') 
MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY', '') 