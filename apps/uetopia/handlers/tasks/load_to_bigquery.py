import webapp2
import logging
import uuid
from google.appengine.api import taskqueue
import cloudstorage as gcs
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from configuration import *

class LoadToBigQueryHandler(webapp2.RequestHandler):
    def post(self):
        credentials = GoogleCredentials.get_application_default()
        self.bigquery = build('bigquery', 'v2', credentials=credentials)

        logging.info("Iterating over bucket...")
        entries = gcs.listbucket('/uetopia-bigquery')


        for entry in entries:
            if "Games.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "Games")

            if "GamePlayers.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "GamePlayers")

            if "GameCharacters.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "GameCharacters")

            if "GamePlayerSnapshot.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "GamePlayerSnapshot")

            if "MatchPlayers.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "MatchPlayers")

            if "Match.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "Match")

            if "Tournaments.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "Tournaments")

            if "Transactions.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "Transactions")

            if "Users.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "Users")

            if "ServerInstances.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "ServerInstances")

            if "EventFeed.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "EventFeed")

            if "Servers.backup_info" in entry.filename:
                self.submit_bigquery_job(entry.filename, "Servers")




        return
    def submit_bigquery_job(self, filename, tableId):
        logging.info('gs:/{}'.format(filename))
        job_data = {
            'jobReference': {
                'projectId': 'ue4topia',
                'job_id': str(uuid.uuid4())
            },
            'configuration': {
                'load': {
                    'sourceUris': ['gs:/{}'.format(filename)],
                    'sourceFormat': 'DATASTORE_BACKUP',
                    'writeDisposition': 'WRITE_TRUNCATE',
                    'destinationTable': {
                        'projectId': 'ue4topia',
                        'datasetId': 'DailyExport',
                        'tableId': tableId
                    }
                }
            }
        }

        response = self.bigquery.jobs().insert(
            projectId='ue4topia',
            body=job_data).execute(num_retries=3)

        logging.info(response)
