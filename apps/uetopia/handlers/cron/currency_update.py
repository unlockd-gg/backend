import logging
import re
import string
import datetime
from apps.handlers import BaseHandler
from google.appengine.api import users
from google.appengine.api import taskqueue
from apps.uetopia.controllers.currency import CurrencyController
from openexchangerates import OpenExchangeRatesClient
from configuration import *

class CronCurrencyUpdateHandler(BaseHandler):
    """
    Get latest currency values

    """
    def post(self):
        return self.get()

    def get(self):

        cController = CurrencyController()

        client = OpenExchangeRatesClient(OPENEXCHANGERATES_APPID)
        currencies = client.currencies()

        #logging.info(currencies)


        #latest_rates = client.latest(base='BTC')
        latest_rates = client.latest()

        logging.info(latest_rates)

        for currency in currencies:
            #logging.info(currency)
            #logging.info(currencies[currency])

            if str(currency) == 'BTC':

                db_currency = cController.get_by_iso_code(currency)

                if not db_currency:
                    str_rate = latest_rates['rates'][currency]
                    rate = float(str_rate)
                    cController.create(
                        title = currencies[currency],
                        iso_code = currency,
                        value_to_usd = rate
                    )
                else:
                    str_rate = latest_rates['rates'][currency]
                    rate = float(str_rate)
                    #str_rate = string.strip(str_rate,"""Decimal('""")
                    logging.info(rate)
                    db_currency.value_to_usd = rate
                    cController.update(db_currency)

                ## update firebase
                taskUrl='/task/currency/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', countdown = 2,)
