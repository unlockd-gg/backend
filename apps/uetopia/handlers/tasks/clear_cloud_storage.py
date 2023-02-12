import webapp2
import logging
import uuid
from google.appengine.api import taskqueue
import cloudstorage as gcs
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from configuration import *

class ClearCloudStorageHandler(webapp2.RequestHandler):
    def post(self):
        credentials = GoogleCredentials.get_application_default()
        bigquery = build('bigquery', 'v2', credentials=credentials)

        logging.info("Iterating over bucket...")
        entries = gcs.listbucket('/uetopia-bigquery')

        for entry in entries:
            gcs.delete(entry.filename)

        return
