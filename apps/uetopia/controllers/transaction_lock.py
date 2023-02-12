import logging
import datetime
from google.appengine.api import memcache
from configuration import *

## THIS IS NOT A STANDARD DATABASE CONTROLLER
## THIS IS MEMCACHE

class TransactionLockController:
    """TransactionLockController Controller"""

    def get(self, parentKey):
        """ get memcached data """

        data = memcache.get(parentKey)
        return data

    def set(self, parentKey):
        """ set the latest time """
        memcache.set(parentKey, datetime.datetime.now())
        return

    def pushable(self, parentKey, seconds=None):
        """ True if the channel has not had a push recently """
        data = self.get(parentKey)
        if data is not None:
            now = datetime.datetime.now()
            if seconds:
                seconds_t = datetime.timedelta(seconds=seconds)
                earlier = now - seconds_t
            else:
                earlier = now - SERVER_TRANSACTION_QUEUE_MINIMUM_INTERVAL
            if data > earlier:
                return False
            else:
                self.set(parentKey)
                return True
        else:
            self.set(parentKey)
            return True
