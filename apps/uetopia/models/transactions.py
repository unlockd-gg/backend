import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types


class Transactions(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    amountInt = ndb.IntegerProperty(indexed=False) ## actual CRED amount minus uetopia fees
    amount = ndb.FloatProperty(indexed=False) # for display
    amountIntGross = ndb.IntegerProperty(indexed=False)  ## original gross amount for gross income calculations

    newBalanceInt = ndb.IntegerProperty(indexed=False)
    newBalance = ndb.FloatProperty(indexed=False) # for display

    description = ndb.StringProperty(indexed=False)
    userKeyId = ndb.IntegerProperty()
    firebaseUser = ndb.StringProperty()

    targetUserKeyId = ndb.IntegerProperty()


    serverKeyId = ndb.IntegerProperty(indexed=True)
    serverTitle = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty(indexed=True)
    gameTitle = ndb.StringProperty(indexed=False)

    groupKeyId = ndb.IntegerProperty(indexed=True)
    groupTitle = ndb.StringProperty(indexed=False)

    tournamentKeyId = ndb.IntegerProperty(indexed=True)
    tournamentTitle = ndb.StringProperty(indexed=False)

    vendorKeyId = ndb.IntegerProperty(indexed=True)
    vendorTitle = ndb.StringProperty(indexed=False)

    adKeyId = ndb.IntegerProperty(indexed=True)
    adTitle = ndb.StringProperty(indexed=False)

    ## transactions for serverplayers
    serverPlayerKeyId = ndb.IntegerProperty()

    ##  transactions are batched and processed all at once.
    transactionType = ndb.StringProperty(indexed=True) ## user, server, game, tournament
    transactionClass = ndb.StringProperty(indexed=True) ## donation, payment,
    transactionSender = ndb.BooleanProperty(indexed=True)
    transactionRecipient = ndb.BooleanProperty(indexed=True)
    recipientTransactionKeyId = ndb.IntegerProperty(indexed=True) ## pair transactions in case we need to roll one back.
    submitted = ndb.BooleanProperty(indexed=True)
    processed = ndb.BooleanProperty(indexed=True)

    materialIcon = ndb.StringProperty(indexed=False)
    materialDisplayClass = ndb.StringProperty(indexed=False)


    #transaction_hash = ndb.StringProperty()
    #confirmations = ndb.IntegerProperty()

    def to_json(self):
        return ({
            u'key_id':self.key.id(),
            u'amountInt':self.amountInt,
            u'newBalanceInt':self.newBalanceInt,
            u'description':self.description,
            u'created':self.created.isoformat(' ')
        })

### PROTORPC MODELS FOR ENDPOINTS


class TransactionResponse(messages.Message):
    """ a transaction's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    amountInt = messages.IntegerField(2, variant=messages.Variant.INT32)
    newBalanceInt = messages.IntegerField(3, variant=messages.Variant.INT32)
    description = messages.StringField(4)
    created = messages.StringField(6)
    transactionClass = messages.StringField(7)
    transactionType = messages.StringField(8)
    materialIcon = messages.StringField(9)
    materialDisplayClass = messages.StringField(10)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)

class TransactionCollection(messages.Message):
    """ multiple transactions """
    transactions = messages.MessageField(TransactionResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)

class TransactionRequest(messages.Message):
    """ a Transaction updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    amountInt = messages.IntegerField(2, variant=messages.Variant.INT32)
    transactionType = messages.StringField(3)
    transactionClass = messages.StringField(4)
    serverKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    targetUserKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    fromGroup = messages.BooleanField(10)
    fromGroupKeyId = messages.IntegerField(11, variant=messages.Variant.INT32)


TRANSACTION_RESOURCE = endpoints.ResourceContainer(
    TransactionRequest
)

class BitPayInvoiceRequest(messages.Message):
    """ a bitpay invoice updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    amountBTC = messages.FloatField(2)

BITPAY_INVOICE_RESOURCE = endpoints.ResourceContainer(
    BitPayInvoiceRequest
)

class TransactionCollectionPageRequest(messages.Message):
    """ a transaction collection's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    transactionType = messages.StringField(4)
    userKeyId = messages.IntegerField(18)
    serverKeyId = messages.IntegerField(19)
    gameKeyId = messages.IntegerField(20)
    groupKeyId = messages.IntegerField(21)

TRANSACTION_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    TransactionCollectionPageRequest
)

class BitPayInvoiceResponse(messages.Message):
    """ a transaction's data """
    invoice = messages.IntegerField(1, variant=messages.Variant.INT32)
    bitpayurl = messages.StringField(2)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)

class BraintreeTokenRequest(messages.Message):
    """ a bitpay invoice updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    payment_method_nonce = messages.StringField(2)
    amountUSD = messages.FloatField(3)

BRAINTREE_TOKEN_RESOURCE = endpoints.ResourceContainer(
    BraintreeTokenRequest
)

class BraintreeTokenResponse(messages.Message):
    """ a transaction's data """
    #invoice = messages.IntegerField(1, variant=messages.Variant.INT32)
    token = messages.StringField(2)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(41)
