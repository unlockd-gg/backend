import datetime
import httplib
import json
import webapp2
import logging
import uuid
from google.appengine.api import taskqueue
import cloudstorage as gcs
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from google.appengine.api import app_identity
from google.appengine.api import urlfetch

from configuration import *

class BigQueryTasksStartHandler(webapp2.RequestHandler):
    def get(self):

        access_token, _ = app_identity.get_access_token('https://www.googleapis.com/auth/datastore')
        app_id = app_identity.get_application_id()
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

        output_url_prefix = 'gs://uetopia-bigquery'

        assert output_url_prefix and output_url_prefix.startswith('gs://')
        if '/' not in output_url_prefix[5:]:
            # Only a bucket name has been provided - no prefix or trailing slash
            output_url_prefix += '/' + timestamp
        else:
            output_url_prefix += timestamp

        entity_filter = {
            'kinds': ['Games', 'GamePlayers', 'GameCharacters', 'GamePlayerSnapshot', 'MatchPlayers', 'Match', 'Tournaments', 'Transactions', 'Users', 'Servers', 'ServerInstances', 'EventFeed'],
            'namespace_ids': []
        }
        request = {
            'project_id': app_id,
            'output_url_prefix': output_url_prefix,
            'entity_filter': entity_filter
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        url = 'https://datastore.googleapis.com/v1/projects/%s:export' % app_id
        try:
            result = urlfetch.fetch(
                url=url,
                payload=json.dumps(request),
                method=urlfetch.POST,
                deadline=60,
                headers=headers)
            if result.status_code == httplib.OK:
                logging.info(result.content)
            elif result.status_code >= 500:
                logging.error(result.content)
            else:
                logging.warning(result.content)
            self.response.status_int = result.status_code
        except urlfetch.Error:
            logging.exception('Failed to initiate export.')
            self.response.status_int = httplib.INTERNAL_SERVER_ERROR


        ## OLD WAY
        """
        ## Fire off a task for backing up the current datastore

        task = taskqueue.add(
        url='/_ah/datastore_admin/backup.create',
        method='GET',
        queue_name="mapreduce",
        params={
            'filesystem': 'gs',
            'gs_bucket_name': 'uetopia-bigquery',
            'kind': ['Games', 'GamePlayers', 'GameCharacters', 'GamePlayerSnapshot', 'MatchPlayers', 'Match', 'Tournaments', 'Transactions', 'Users', 'Servers', 'ServerInstances', 'EventFeed']
        }
    )
        """

        ## Then, later after this is done, we want a task to load that data into bigquery

        taskUrl='/task/bigquery/load'
        taskqueue.add(url=taskUrl, queue_name='bigqueryDataPipeline', countdown=600)

        ## Then after that is done we want to clear out the cloud storage bucket

        taskUrl='/task/cloudstorage/clear'
        taskqueue.add(url=taskUrl, queue_name='bigqueryDataPipeline', countdown=1200)


        return
