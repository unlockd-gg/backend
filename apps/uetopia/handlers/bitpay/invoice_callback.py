import logging
import re
import string
import datetime
from apps.handlers import BaseHandler

import requests
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

from google.appengine.api import users
from google.appengine.api import taskqueue
#from apps.uetopia.controllers.currency import CurrencyController
from openexchangerates import OpenExchangeRatesClient

from apps.uetopia.controllers.orders import OrdersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

## https://bitpay.com/docs/invoice-callbacks

class BitPayInvoiceCallbackHandler(BaseHandler):
    """
    Bitpay is notifying us that an invoice status has changed.
    https://bitpay.com/docs/invoice-callbacks

    """
    def post(self):
        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        ## get the invoiceId

        bitpayInvoiceId = jsonobject['id']
        logging.info(bitpayInvoiceId)

        ## presumably the "posData" is in here too?

        ## check with bitpay directly

        bitpay_invoice_url = "https://bitpay.com/invoice?id=" + bitpayInvoiceId

        headers = {"Content-Type": "application/json"}

        payload = {
                  "price": value_in_btc,
                  "currency": "BTC",
                  "posData": str(order.key.id()),
                  "notificationURL": BITPAY_NOTIFICATION_URL,
                  "buyerEmail": authorized_user.email
                  }

        response = requests.get(bitpay_invoice_url, auth=(BITPAY_API_KEY_ID, ''))

        logging.info(response.status_code)
        response_json = response.json()
        logging.info(response_json)

        ## get the status
        bitpay_status = response_json['status']
        logging.info(bitpay_status)
        if bitpay_status == "confirmed":
            ## we need the posData which contains our local order keyId.
            bitpay_order_number = response_json['posData']
            logging.info('bitpay_order_number: %s' %bitpay_order_number)

            orderController = OrdersController()

            bitpay_order = orderController.get_by-Key_id(int(bitpay_order_number))

            if not bitpay_order:
                logging.error('this bitpay order could not be found')
                return

            ## update the order as paid
            bitpay_order.status_confirmed = True
            orderController.update(bitpay_order)

            ## create the transaction
            description = "CRED purchase via BitPay"

            ## Create a transaction for the deposit -user
            transaction = TransactionsController().create(
                userKeyId = bitpay_order.userKeyId,
                firebaseUser = bitpay_order.firebaseUser,
                description = description,
                ##confirmations = 0,
                amountInt = bitpay_order.value_in_cred,
                #serverKeyId = server.key.id(),
                #serverTitle = server.title,
                ##amount = currency_hold / 100000000. * -1,
                #newBalanceInt = authorized_user.currencyBalance,
                #newBalance = float(authorized_user.currencyBalance) / 100000000.
                transactionType = "user",
                transactionClass = "CRED purchase",
                transactionSender = False,
                transactionRecipient = True,
                submitted = True,
                processed = False,
                materialIcon = MATERIAL_ICON_CRED_PURCHASE,
                materialDisplayClass = "md-primary"
                )



            pushable = lockController.pushable("user:%s"%bitpay_order.userKeyId)
            if pushable:
                logging.info('user pushable')
                taskUrl='/task/user/transaction/process'
                taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                    "key_id": bitpay_order.userKeyId
                                                                                }, countdown=2)
        ## todo maybe post an alert when it is paid...
        return
