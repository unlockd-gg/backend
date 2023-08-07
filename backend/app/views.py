from flask import Flask
from flask import send_file
from flask import render_template
from flask import request, make_response
from flask import jsonify
from flask_cors import CORS
from datetime import datetime
from base64 import encodebytes, b64encode
from base64 import encodebytes
from bson.objectid import ObjectId
from bson import json_util
import io
import string
import http.client

from . import app
from app.models import users
from app.models import lightningwallets
from app.models import lightningchallenges

#import docker
import pyqrcode
import secrets
import socket
import pymongo  # package for working with MongoDB
import logging
import jwt
import os
import random
from sys import stdout

from functools import wraps

from app.bech import encode_string
from app.der import decode_signature

from app.ecc import elliptic_curve
from app.ecc import ecdsa
from app.ecc import point,hex_to_int

from .settings import *

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(stdout)
console.setLevel(level=logging.DEBUG)
formatter =  logging.Formatter('%(levelname)s : %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
# does not work
#if __name__ != '__main__':
gunicorn_logger = logging.getLogger('gunicorn.debug')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(gunicorn_logger.level)

#onion_address = "yri5o7gtfa4yabmroogtiyqbulw4g4to3zukuwezpf3er6ifhy5bwcyd.onion"

## move this to mongo
#challenges = []

G = point(
    hex_to_int("79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798"),
    hex_to_int("483ADA77 26A3C465 5DA4FBFC 0E1108A8 FD17B448 A6855419 9C47D08F FB10D4B8")
)

secp256k1 = elliptic_curve(
    0,
    7,
    hex_to_int("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE FFFFFC2F"),
    hex_to_int("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141"),
    G
)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")

@app.route("/auth")
def auth():
    logger.debug('Auth')
    #32 byte challenge k1
    k1 = secrets.token_hex(32)
    #host_address = socket.gethostbyname(socket.gethostname())
    host_address = "unlockd.gg"
    #client = docker.DockerClient()
    #container = client.containers.get('fplb')
    #host_address = container.attrs['NetworkSettings']['IPAddress']
    url = "https://"+host_address+"/api/signin?tag=login&k1="+k1
    print(url)

    #add k1 to challenges
    # store in db instead
    #challenges.append(k1)
    lightning_challenge_model = lightningchallenges.LightningChallenges()
    
    #bech32 encode string
    bech_32_url = encode_string(url)
    lightning_challenge_model.create({"k1": k1, "bech_32_url": bech_32_url})

    #response = {'lnurl': bech_32_url}
    return jsonify({'lnurl' : bech_32_url})

@app.route("/signin")
def signin():

    ## This gets called by the lightning network.

    user_model = users.Users()
    lightning_wallet_model = lightningwallets.LightningWallets()
    lightning_challneges_model = lightningchallenges.LightningChallenges()

    error = {
        "status" : False,
        "message" : None
    }

    #long hex string --> r: INT,Base 10: s: INT,Base 10
    der_sig = request.args.get("sig")
    #compressed public key needs to be encodeded
    public_key = ecdsa.compressed_to_point(request.args.get("key"),secp256k1)
    k1 = request.args.get("k1")
    logger.debug("sig k1: "+k1)
    if der_sig == None or public_key == None or k1 == None:
        error["status"] = True
        error["message"] = "P_K,Sig or k1 misssing"

    ## look up the k1 from the db
    ## we don't have the public key yet, so use the k1
    print(k1)
    print(public_key.__str__())
    pending_challenge = lightning_challneges_model.find_by_k1(k1)
    print(pending_challenge)

    if pending_challenge is None:
        print('Challenge not found')
        error["status"] = True
        error["message"] = "Invalid challenge"
    else:
        print('found challenge')
        ## do we really want to delete it?
        ## Yes this is just a challenge. Delete it.  But do it in the return area after we are done.
        # We do want to keep track of the public key here.

        ## Check to see if the public key is already registered.
        ##   If so, get the user for this key
        ##     If user exists, mark online
        ##     If not, prompt the user to connect to an email address, and begin email verification 
        ##   If no public key is found, create one, and begin email verification

        existing_wallet = lightning_wallet_model.find_by_publickey(public_key.__str__())
        print(existing_wallet)

        if existing_wallet is None:
            print('existing wallet not found - creating')

            new_wallet = lightning_wallet_model.create(
                {
                    "publickey": public_key.__str__(), 
                    "userid": "0",
                    "userconnected": False,
                    "emailaddress": "",
                    "emailvalidated": False,
                    "k1": k1,
                    "bech_32_url": pending_challenge["bech_32_url"],

                 }
            )
        else:
            print('found existing wallet')

            ## TODO update with this challenge's bech_32_url
            existing_wallet['bech_32_url'] = pending_challenge['bech_32_url']
            lightning_wallet_model.update(existing_wallet['_id'], existing_wallet)
            
            if existing_wallet['userconnected']:
                print('user connected')
                user = user_model.find_by_id(existing_wallet['userid'])

                
                if user:
                    ## do we need to do something with the user?
                    print('got user')

                else:
                    print('user not found')

                    ## TODO send out an email verification - but we don't have the email yet... 

            else:
                print('user not connected')

            

    try:
        sig = decode_signature(der_sig)
    except:
        sig = None
        error["status"] = True
        error["message"] = "signature not encoded right"

    try:
        sig_status = ecdsa.raw_verify(public_key,k1,sig,secp256k1)
        if sig_status == False:
            error["status"] = True
            error["message"] = "Signature is invalid"
    except:
        error["status"] = True
        error["message"] = "Signature validation failed"


    if error["status"] == True:
        print(error['message'])
        return jsonify(
            status="ERROR",
            reason=error["message"]
        )
    else:
        # delete the pending challenge 
        lightning_challneges_model.delete(pending_challenge["_id"])
        return jsonify(
            status = "OK",
            event = "LOGGEDIN"
        )

@app.route("/generate_qr/<bech_32_url>")
def generate_qr(bech_32_url = None):
    #save as url code and send

    # https://github.com/chill117/passport-lnurl-auth
    # The URI schema prefix used before the encoded LNURL.
    # e.g. "lightning:" or "LIGHTNING:" or "" (empty-string)
    uriSchemaPrefix = "LIGHTNING:"

    # https://github.com/mnooner256/pyqrcode/issues/39#issuecomment-207621532
    # c = pyqrcode.create("hello")
    # s = io.BytesIO()
    # c.png(s,scale=6)
    # encoded = base64.b64encode(s.getvalue()).decode("ascii")


    qr = pyqrcode.create(uriSchemaPrefix+bech_32_url.upper())
    s = io.BytesIO()
    qr.png(s, scale=6)
    encoded = b64encode(s.getvalue()).decode("ascii")

    #qr.svg("ln-auth-challenge.svg",scale=8)
    #return send_file("../ln-auth-challenge.svg",mimetype="image/svg+xml")
    return s.getvalue()

@app.route("/me")
def me():
    #print(request.__dict__)
    ## TODO look this wallet up from the database
    ## assuming here we have a pubkey, but we can use the challenge url again
    ## or maybe we can use session?

    ## for now, just using the intial bech_32_url aka challenge url
    bech_32_url = request.args.get("bech_32_url") # or ""
    print(bech_32_url)

    user_model = users.Users()
    lightning_wallet_model = lightningwallets.LightningWallets()
    lightning_challneges_model = lightningchallenges.LightningChallenges()

    this_wallet = lightning_wallet_model.find_by_bech_32_url(bech_32_url)

    if this_wallet == None:
        print('did not find wallet by bech_32_url')

    else:
        print('found wallet by bech_32_url')

        if this_wallet['userid'] == "0":
            print('user id set to zero')
            auth_token = lightning_wallet_model.encode_auth_token(str(this_wallet['_id']))
            print(auth_token)
            if auth_token:
                responseObject = {
                    'userid': 0,
                    'name': 'anonymous user',
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token,
                    'do_email_validation': True
                }
                return make_response(jsonify(responseObject)), 200
        else:
            ## does not work.  bson.errors.InvalidId: 'Inserted Id 6497c62cd0c61bafbd399a27' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string
            #objInstance = ObjectId(this_wallet['userid'])

            user = user_model.find_by_id(ObjectId(this_wallet['userid']))  
            if user == None:
                print('user not found')
                auth_token = lightning_wallet_model.encode_auth_token(str(this_wallet['_id']))
                print(auth_token)
                if auth_token:
                    responseObject = {
                        'userid': 0,
                        'name': 'anonymous user',
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token,
                        'do_email_validation': True
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                print('found user')
                ## generate an auth token
                auth_token = lightning_wallet_model.encode_auth_token(str(this_wallet['_id']))
                print(auth_token)
                if auth_token:
                    responseObject = {
                        'userid': str(user['_id']),
                        'name': 'anonymous user',
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token,
                        'do_email_validation': False
                    }
                    return make_response(jsonify(responseObject)), 200
        #except:
        #    logger.debug('did not find userid in wallet.  Is login complete?')
            
    responseObject = {
        'status': 'fail',
        'message': 'Login process incomplete'
        }
    return make_response(jsonify(responseObject)), 200


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_model = users.Users()
        lightning_wallet_model = lightningwallets.LightningWallets()
        token = None
        # jwt is passed in the request header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            print('found Auth header')
            token = auth_header.split(" ")[1]

        print(token)

        #if 'x-access-token' in request.headers:
        #    print('found x-access-token')
        #    token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        #try:
        # decoding the payload to fetch the stored details
        data = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

        print(data)

        wallet = lightning_wallet_model.find_by_id(ObjectId(data['sub']))
        if wallet != None:
            logger.debug('found wallet')

            ## at this point, we might not have a user yet.
            #current_user = user_model.find_by_id(wallet['userid'])
            #if current_user:
            #    logger.debug('found current_user')

        #except:
        #    return jsonify({
        #        'message' : 'Token is invalid !!'
        #    }), 401
        # returns the current logged in users context to the routes
        return  f(wallet, *args, **kwargs)
  
    return decorated

## TODO Create admin_token_required wrapper

@app.route("/user/email/<incoming_email>/start")
@token_required
def userEmailValidationStart(wallet, incoming_email = None):
    lightning_wallet_model = lightningwallets.LightningWallets()

    # start the email validation process.
    print(incoming_email)

    # get the wallet from the decorator
    print(wallet)

    ## TODO make sure email is not already validated?
    
    #update the email address to the supplied
    #wallet['emailaddress'] = incoming_email

    # TODO generate a verification code
    randomInt = str(random.randint(100000, 999999))

    lightning_wallet_model.update(wallet['_id'], {'emailaddress': incoming_email, 'emailverificationcode': randomInt})

    # send an email containing the verification code and link

    return jsonify({'success' : True})

@app.route("/user/email/<incoming_email>/validate/<incoming_validation>")
@token_required
def userEmailValidationComplete(wallet, incoming_email = None, incoming_validation = None):
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    # start the email validation process.
    print(incoming_email)
    print(incoming_validation)

    # get the wallet from the decorator
    print(wallet)

    if wallet['emailverificationcode'] == incoming_validation:
        print('validation match')

        ## look up user by email
        user = user_model.find_by_emailaddress(incoming_email)
        if user is None:
            print('user not found - creating')
            user = user_model.create({'emailaddress': incoming_email})
            lightning_wallet_model.update(wallet['_id'], { 'userid': user, 'userconnected': True })
        else:
            print('found user with this email')
            lightning_wallet_model.update(wallet['_id'], { 'userid': user['_id'], 'userconnected': True })

    else:
        print('validation mismatch')
        return jsonify({'success' : False})

    return jsonify({'success' : True})


## Login support for regular email and no lightning
@app.route("/user/email/<incoming_email>/start-no-lightning")
def userEmailValidationStartNoLightning(incoming_email = None):
    lightning_wallet_model = lightningwallets.LightningWallets()

    # start the email validation process.
    print(incoming_email)

    # create a fake wallet

    # initializing size of string
    N = 64
    
    # using random.choices()
    # generating random strings
    fake_pub_key = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    
    fake_k1 = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    
    fake_bech_32_url = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    

    randomInt = str(random.randint(100000, 999999))

    new_wallet = lightning_wallet_model.create(
                {
                    "publickey": fake_pub_key,
                    "userid": "0",
                    "userconnected": False,
                    "emailaddress": incoming_email,
                    "emailverificationcode": randomInt,
                    "emailvalidated": False,
                    "k1": fake_k1,
                    "bech_32_url": fake_bech_32_url,
                    "fakewallet": True

                 }
            )


    # send an email containing the verification code and link


    return jsonify({'success' : True, 
                    'publickey': fake_pub_key,
                    'k1': fake_k1,
                    'bech_32_url':fake_bech_32_url    })

@app.route("/user/email/<incoming_email>/validate-no-lightning/<incoming_validation>/<incoming_fake_pub_key>")
def userEmailValidationCompleteNoLightning(incoming_email = None, incoming_validation = None, incoming_fake_pub_key = None):
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    # start the email validation process.
    print(incoming_email)
    print(incoming_validation)

    # look up the fake wallet from the generated pubkey
    ## TODO - set up a cron job to delete these

    print(incoming_fake_pub_key)

    fakewallet = lightning_wallet_model.find_by_publickey(incoming_fake_pub_key)

    if fakewallet == None:
        print('fake wallet not found')
    else:
        print('found fake wallet')

        if fakewallet['emailverificationcode'] == incoming_validation:
            print('validation match')

            ## look up user by email
            user = user_model.find_by_emailaddress(incoming_email)
            if user is None:
                print('user not found - creating')
                newuser_id = user_model.create({'emailaddress': incoming_email

                                        })
                lightning_wallet_model.update(fakewallet['_id'], { 'userid': newuser_id, 'userconnected': True })

                ## get the user we just created, and replace the previous user that did not exist
                user = user_model.find_by_id(ObjectId(newuser_id))

                ## Send a msg to discord

            else:
                print('found user with this email')
                lightning_wallet_model.update(fakewallet['_id'], { 'userid': user['_id'], 'userconnected': True })

            ## generate an auth token
            auth_token = lightning_wallet_model.encode_auth_token(str(fakewallet['_id']))
            print(auth_token)
            if auth_token:
                responseObject = {
                    'success' : True,
                    #'userid': str(user['_id']),
                    'name': 'anonymous user',
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token,
                    'do_email_validation': False,
                    'user':  user_model.to_json(user)
                }
                return make_response(jsonify(responseObject)), 200

        else:
            print('validation mismatch')
            return jsonify({'success' : False})

    return jsonify({'success' : False})



@app.route("/setup_database")
def setup_database():
    ## TODO check for admin superuser
    
    # first drop any previous entries
    ## todo remove this for production 
    ## This is not working in production - command dropDatabase requires authentication
    ## instead we can clean up manually
    #mongo_client = pymongo.MongoClient('mongodb://mongo:27017')
    #mongo_client.drop_database('customersdb');

    lightning_wallet_model = lightningwallets.LightningWallets()
    wallets = lightning_wallet_model.find({})
    for wallet in wallets:
        print('found wallet')
        #lightning_wallet_model.delete(wallet['_id'])


    user_model = users.Users()
    site_users = user_model.find({})
    for site_user in site_users:
        print('found user')
        #user_model.delete(site_user['_id'])
        user_model.update(site_user['_id'], {'admin': True})

    """

    # setup model(s)
    user_model = users.Users()

    user_list = [
    { "name": "Amy", "address": "Apple st 652"},
    { "name": "Hannah", "address": "Mountain 21"},
    { "name": "Michael", "address": "Valley 345"},
    { "name": "Sandy", "address": "Ocean blvd 2"},
    { "name": "Betty", "address": "Green Grass 1"},
    { "name": "Richard", "address": "Sky st 331"},
    { "name": "Susan", "address": "One way 98"},
    { "name": "Vicky", "address": "Yellow Garden 2"},
    { "name": "Ben", "address": "Park Lane 38"},
    { "name": "William", "address": "Central st 954"},
    { "name": "Chuck", "address": "Main Road 989"},
    { "name": "Viola", "address": "Sideway 1633"}
    ]
    for user_data in user_list:
        user_model.create(user_data)

    lightning_challneges_model = lightningchallenges.LightningChallenges()
    lightning_challneges_model.create({"k1": "1"})
    lightning_challneges_model.create({"k1": "2"})
    lightning_challneges_model.create({"k1": "3"})
    lightning_challneges_model.create({"k1": "4"})

    lightning_wallet_model = lightningwallets.LightningWallets()
    lightning_wallet_model.create({"publickey": "1"})
    """

    return jsonify({'success' : True})


## Views for data validation and testing
## Todo - after roles and permissions are in, these should be protected by them

#@app.route("/users/")
#def users_list():
#    # setup model(s)
#    user_model = users.Users()
#    return jsonify(user_model.find({})), 200

#@app.route("/lightning/challenges")
#def challenge_list():
#    # setup model(s)
#    lightning_challneges_model = lightningchallenges.LightningChallenges()
#    return jsonify(lightning_challneges_model.find({})), 200

#@app.route("/lightning/wallets")
#def wallet_list():
#    # setup model(s)
#    lightning_wallet_model = lightningwallets.LightningWallets()
#    return jsonify( json_util.dumps(lightning_wallet_model.find({}) )), 200

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response


## Actual API endpoints


@app.route("/users/profile/update", methods = ['POST'])
@token_required
def user_profile_update(wallet):
    print('user profile update')
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        # get the wallet from the decorator
        print(wallet)

        print(json.get('title'))

        # check if the wallet is connected to a user
        if wallet['userconnected']: 
            print('user connected')

            # get the user
            user = user_model.find_by_id(ObjectId(wallet['userid']))
            
            if user == None:
                print('did not find user')
            else:
                print('found user')
                print(user)
                print(json.get('title'))

                ## default response
                response_message="Success."
                response_title = "Success"

                ##  update the database
                user_model.update(user['_id'], 
                                  {'title': json.get('title'),
                                   
                                   
                                    })
                user['title'] = json.get('title')
                result = jsonify({'success' : True,
                                'user':  user_model.to_json(user),
                                'response_message': response_message,
                                'response_title': response_title
                                })
                print(result)


                return result
            
    print('returning failure')

    return jsonify({'success' : False,
                    'user':  user_model.to_json(user)
                    })
        

    
@app.route("/users/data", methods = ['POST', 'GET'])
@token_required
def user_data(wallet):
    print('user data')
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    print(wallet)

    # check if the wallet is connected to a user
    if wallet['userconnected']: 
        print('user connected')

        # get the user
        user = user_model.find_by_id(ObjectId(wallet['userid']))
        
        if user == None:
            print('did not find user')
        else:
            print('found user')
            print(user)

            #print(build_frontend_user_json(user) )
            result = jsonify({'success' : True,
                            'user': user_model.to_json(user)
                            })
            print(result)
            return result
            
    print('returning failure')

    return jsonify({'success' : False,
                    'user':  None
                    })
        


###################################
## USERS
###################################

@app.route("/users/")
@token_required
def users_list(wallet):
    print('get users')
    # setup model(s)
    user_model = users.Users()

    # check if the wallet is connected to a user
    if wallet['userconnected']: 
        print('user connected')

        # get the user
        user = user_model.find_by_id(ObjectId(wallet['userid']))
        
        if user == None:
            print('did not find user')
        else:
            print('found user')

            ## get the role for this user
            if user['admin']:
                print('user is admin')

                return jsonify(user_model.find({})), 200
            
    return jsonify({'success' : False,
                    'users': {}
                    })


@app.route("/admin/users/<userid>", methods = ['GET','POST'])
@token_required
def user_get(wallet, userid = None):
    print('get user')
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    #content_type = request.headers.get('Content-Type')
   # if (content_type == 'application/json'):
    #    json = request.json

    # get the wallet from the decorator
    print(wallet)

    ## roleid is in the request args
    print(userid)

    # check if the wallet is connected to a user
    if wallet['userconnected']: 
        print('user connected')

        # get the user
        user = user_model.find_by_id(ObjectId(wallet['userid']))
        
        if user == None:
            print('did not find user')
        else:
            print('found user')

            ## get the role for this user
            if user['admin']:
                print('user is admin')

                print(userid)

                thisuser = user_model.find_by_id(ObjectId(userid))

                if thisuser == None:
                    print('requested user not found by userid')
                else:
                    result = jsonify({'success' : True,
                        'user': user_model.to_json(thisuser)
                        })
                    print(result)
                    return result

    print('returning failure')

    return jsonify({'success' : False,
                    'user': {}
                    })


@app.route("/admin/users/<userid>/update", methods = ['POST'])
@token_required
def user_update(wallet, userid=None):
    print('update user')
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        # get the wallet from the decorator
        print(wallet)

        # check if the wallet is connected to a user
        if wallet['userconnected']: 
            print('user connected')

            # get the user
            user = user_model.find_by_id(ObjectId(wallet['userid']))
            
            if user == None:
                print('did not find user')
            else:
                print('found user')

                ## get the role for this user
                if user['admin']:
                    print('user is admin')

                    print(userid)

                    thisuser = user_model.find_by_id(ObjectId(userid))

                    if thisuser == None:
                        print('requested user not found by userid')
                    else:

                        newuser = user_model.update(userid, {
                            "title": json.get('title'),
                            "emailaddress": json.get('emailaddress'),
                            "developer": json.get('developer'),
                            

                        })

                        result = jsonify({'success' : True,
                            'user': newuser
                            })
                        print(result)

                        ## TODO Send a msg to discord
                        

                        return result
                            
    print('returning failure')

    return jsonify({'success' : False,
                    'user': {}
                    })


@app.route("/admin/users/<userid>/delete", methods = ['POST'])
@token_required
def user_delete(wallet, userid=None):
    print('delete user')
    lightning_wallet_model = lightningwallets.LightningWallets()
    user_model = users.Users()

    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        # get the wallet from the decorator
        print(wallet)

        # check if the wallet is connected to a user
        if wallet['userconnected']: 
            print('user connected')

            # get the user
            user = user_model.find_by_id(ObjectId(wallet['userid']))
            
            if user == None:
                print('did not find user')
            else:
                print('found user')

                ## get the role for this user
                if user['admin']:
                    print('user is admin')

                    print(userid)

                    thisuser = user_model.find_by_id(ObjectId(userid))

                    if thisuser == None:
                        print('requested user not found by userid')
                    else:

                        user_model.delete(json.get('_id'))

                        result = jsonify({'success' : True
                            })
                        print(result)

                        ## TODO Send a msg to discord

                        return result
            
    print('returning failure')

    return jsonify({'success' : False,
                    'user': {}
                    })
