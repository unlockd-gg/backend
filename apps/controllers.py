import logging
import datetime
import string
import random
import hashlib
import hmac
import json
import urllib
import md5
from google.appengine.ext import ndb
from collections import OrderedDict

class BaseController(object):
    """Base Controller Class - Provides basic database functionality. """
    def __init__(self):

        self._default_order = self.model.created
        self.model = None

    def create(self, **kwargs):
        """ creates a page """
        entity = self.model(**kwargs)
        entity.put()
        return entity

    def list(self):
        """ list all  """
        query = self.model.query()
        return query.fetch(1000)

    def list_page(self, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()

        if filterbytext:
            if filterbytext == 'supported':
                query = query.filter(self.model.supported == True)
            elif filterbytext == 'applied':
                query = query.filter(self.model.applied == True)
            elif filterbytext == 'approved':
                query = query.filter(self.model.approved == True)

        if order:
            query_forward = query.order(order)
            #query_backward = query.order(-order)
        else:
            query_forward = query.order(self.model.key)
            #query_backward = query.order(-self.model.key)

        ecodes, cursor, more = query_forward.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)

        # Fetch the same page going backward.
        #rev_cursor = start_cursor.reversed()
        #bars1, cursor_back, less = query_backward.fetch_page(page_size, start_cursor=rev_cursor, batch_size=batch_size)

        return ecodes, cursor, more#, cursor_back, less


    def get_by_key(self, key):
        """ get an entity by key """
        key = ndb.Key(urlsafe=key)
        return key.get()

    def get_by_key_id(self, key_id):
        """ get an entity by key """

        ##key = ndb.Key(self.model, key_id)
        return self.model.get_by_id(key_id)

    def update(self, entity):
        """ update an entity """
        entity.put()


    def delete(self, entity):
        """Deletes the given entity """

        entity.key.delete()


    def clean_dates(self, start_date, end_date, days=1):
        """ utility method for cleaning up start and end dates """
        if not start_date:
            startdate = datetime.datetime.now()
        else:
            startdate = start_date
        if not end_date:
            future = datetime.timedelta(days=days)
            enddate = startdate + future
        else:
            enddate = end_date
        return startdate, enddate

    def key_generator(self, size=30, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        """ utility method to create keys """
        return ''.join(random.choice(chars) for x in range(size))

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        """ utility method to create id strings """
        return ''.join(random.choice(chars) for x in range(size))


    def int_id_generator(self, size=9, chars=string.digits):
        """ utility method to create id strings.  These are NOT unique and should only be used as a second factor of authentication. """
        return int(''.join(random.choice(chars) for x in range(size)))

    def get_by_api_key(self, apiKey):
        """ get a server by it's api key """
        query = self.model.query()
        query = query.filter(self.model.apiKey == apiKey)
        return query.get()

    def create_unique_authCode(self, size=9, chars=string.digits):
        """ create a unique authCode """
        rebuild = True
        while rebuild:

            authCode = ''.join(random.choice(chars) for x in range(size))
            if self.get_by_authCode(authCode) == None:
                rebuild = False
        return authCode

    def get_by_authCode(self, authCode):
        """ get an entity by it's auth_code """
        query = self.model.query()
        query = query.filter(self.model.authCode == authCode)
        return query.get()

    def create_unique_api_key(self):
        """ create a unique api key """
        rebuild = True
        while rebuild:
            token1 = self.key_generator(size=6)
            token2 = self.key_generator(size=6)
            token3 = self.key_generator(size=6)
            token4 = self.key_generator(size=6)
            key = token1 + "-" + token2 + "-" + token3 + "-" + token4
            if self.get_by_api_key(key) == None:
                rebuild = False
        return key

    def verify_signed_auth(self, request):
        ## Incoming data:
        ######### API authentication ################
        ## API Key from the headers
        ## POST data (?param=val&param1=val1) signed by a shared secret key according to HMAC-SHA512 method;

        apiKey = request.headers['Key']

        logging.info(apiKey)

        ## Get the shared secret associated with this key
        model = self.get_by_api_key(apiKey)
        if model:
            apiSecret = str(model.apiSecret)
        else:
            return False

        signature = request.headers['Sign']

        #logging.info("request.body: %s" % request.body)
        #logging.info("params: ")
        #logging.info(request.arguments())
        #logging.info("Headers: %s" %request.headers)

        ## transitioning to json requests.
        ## check to see if we have json data or not
        if request.get('encryption', None):
            logging.info('found regular arguments!')
            encryption = request.get('encryption')
        else:
            logging.info('found json!')
            jsonstring = request.body
            jsonobject = json.loads(jsonstring)
            encryption = jsonobject["encryption"]


        #params = OrderedDict()
        #for field in request.arguments():
        #    params[field] = request.get(field)

        #sorted_params = OrderedDict(sorted(params.iteritems(), key=lambda x: x[0]))
        sorted_params = request.body

        #sorted_params = urllib.urlencode(sorted_params)
        #logging.info("sorted_params: %s" %sorted_params)

        logging.info("encryption: %s" % encryption)

        # Hash the params string to produce the Sign header value
        if encryption == 'off':
            sign = signature
        elif encryption == 'sha1':
            m = hashlib.sha1
            m.update()
            H = hmac.new(apiSecret, digestmod=hashlib.sha1)
        else:
            H = hmac.new(apiSecret, digestmod=hashlib.sha512)
            H.update(sorted_params)
            sign = H.hexdigest()
        logging.info("sign: %s" %sign)
        logging.info("Hsig: %s" %signature )

        if sign == signature:
            return model
        else:
            return False


    def verify_signed_auth_by_key(self, request):
        ## Incoming data:
        ######### API authentication ################
        ## API Key from the headers
        ## POST data (?param=val&param1=val1) signed by a shared secret key according to HMAC-SHA512 method;

        apiKey = request.headers['Key']

        ## Get the shared secret associated with this key
        model = self.get_by_key(apiKey)
        if model:
            apiSecret = str(model.apiSecret)
        else:
            return False

        signature = request.headers['Sign']
        logging.info("Hsig: %s" %signature )

        logging.info("request.body: %s" % request.body)
        logging.info("params: ")
        logging.info(request.arguments())

        #params = OrderedDict()
        #for field in request.arguments():
        #    params[field] = request.get(field)

        #sorted_params = OrderedDict(sorted(params.iteritems(), key=lambda x: x[0]))
        sorted_params = request.body

        #sorted_params = urllib.urlencode(sorted_params)
        #logging.info("sorted_params: %s" %sorted_params)

        encryption = request.get('encryption', 'sha512')
        logging.info("encryption: %s" % encryption)

        # Hash the params string to produce the Sign header value
        if encryption == 'off':
            sign = signature
        elif encryption == 'sha1':
            m = hashlib.sha1
            m.update()
            H = hmac.new(apiSecret, digestmod=hashlib.sha1)
        else:
            H = hmac.new(apiSecret, digestmod=hashlib.sha512)
            H.update(sorted_params)
            sign = H.hexdigest()

        logging.info("sign: %s" %sign)
        logging.info("Hsig: %s" %signature )

        if sign == signature:
            return model
        else:
            return False

    #def clean_html_post_csv_list(self, str_list, convert=False):
    #    """ take a csv formatted string list and return a proper list """
    #    p_list = []
    #
    #    if str_list:
    #        str_list_split = str_list.split(',')
    #        for x in str_list_split:
    #            str_clean = x.strip()
    #            if len(str_clean) > 0:
    #                if convert:
    #                    if convert == "integer":
    #                        p_list.append(int(x.strip()))
    #                else:
    #                    p_list.append(x.strip())
    #    return p_list
