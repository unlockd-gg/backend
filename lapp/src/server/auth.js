const passport = require("passport");
const lnurlAuth = require("passport-lnurl-auth");
const session = require("express-session");
const { HttpError, verifyAuthorizationSignature } = require("lnurl/lib");
const assert = require("assert");
const crypto = require("crypto");
const lnurl = require("lnurl");
const qrcode = require("qrcode");

const mongoose = require('mongoose');

const lightningChallenge = require('../Models/lightningchallenges.model');
const lightningWallet = require('../Models/lightningwallets.model');

const map = {
  user: new Map(),
  session: new Map(),
};

function setupAuth(app) {
  app.use(
    session({
      secret: "12345",
      resave: false,
      saveUninitialized: true,
    })
  );

  passport.use(
    new lnurlAuth.Strategy(function (linkingPublicKey, done) {
      let user = map.user.get(linkingPublicKey);
      if (!user) {
        user = { id: linkingPublicKey };
        map.user.set(linkingPublicKey, user);
      }
      done(null, user);
    })
  );

  app.use(passport.initialize());
  app.use(passport.session());
  app.use(passport.authenticate("lnurl-auth"));
  passport.serializeUser(function (user, done) {
    done(null, user.id);
  });

  passport.deserializeUser(function (id, done) {
    done(null, map.user.get(id) || null);
  });

  // This is getting called by the frontend first, which returns the challenge
  // Then, is called again through the lightning network, when the user logs in
  
  app.get(
    "/do-login",
    function (req, res, next) {
      next();
    },
    async function (req, res) {
      
      
      if (req.query.k1 || req.query.key || req.query.sig) {
        // Check signature against provided linking public key.
        // This request could originate from a mobile app (ie. not their browser).
        let session;
        assert.ok(
          req.query.k1,
          new HttpError('Missing required parameter: "k1"', 400)
        );
        assert.ok(
          req.query.sig,
          new HttpError('Missing required parameter: "sig"', 400)
        );
        assert.ok(
          req.query.key,
          new HttpError('Missing required parameter: "key"', 400)
        );

        // Look up the k1 from the database
        //const lightning_challenge = await lightningChallenge.findById(id);
        const lightning_challenge = await lightningChallenge.findOne({ k1: req.query.k1 });
        if (!lightning_challenge) {
          new HttpError( 'lightning_challenge does not exist.', 400);
        }

        console.log('challenge found, continuing')

        

        // TODO: get rid of this session stuff.
        //session = map.session.get(req.query.k1);
        //assert.ok(
        //  session,
        //  new HttpError("Secret does not match any known session", 400)
        //);

        // destructure and assign the query vars
        const { k1, sig, key } = req.query;
        // verify signature
        assert.ok(
          verifyAuthorizationSignature(sig, k1, key),
          new HttpError("Invalid signature", 400)
        );

        // Check to see if the public key is already registered.
        const existing_wallet = await lightningWallet.findOne({publickey: key});
        console.log(existing_wallet);

        if (!existing_wallet) {
          console.log('existing wallet not found - creating');

          try {
            const newWallet = new lightningWallet({publickey: key, 
                                                  userid: 0, 
                                                  userconnected: false, 
                                                  emailaddress: '', 
                                                  emailvalidated: false, 
                                                  k1: k1, 
                                                  bech_32_url: lightning_challenge.bech_32_url});
            await newWallet.save();
          } catch (error) {
            console.log('error creating wallet');
            //next(error);
          }
        }
        else {
          console.log('found existing wallet');
          // update with this challenge's bech_32_url so that it can be found by the frontend
          existing_wallet.bech_32_url = lightning_challenge.bech_32_url;
          await existing_wallet.save();
        }

        // TODO: replace this session stuff
        //session.lnurlAuth = session.lnurlAuth || {};
        //session.lnurlAuth.linkingPublicKey = req.query.key;

        // await session.save();  
        return res.status(200).json({ status: "OK" });
    }
      

    // TODO: Replace this session stuff
    // this code initializes and manages session data, including generating and assigning a secret (k1) 
    // to the session and storing it in a map or dictionary for future reference. It helps ensure that session data is properly managed and persists across requests.

    //req.session = req.session || {};
    //req.session.lnurlAuth = req.session.lnurlAuth || {};
    //let k1 = req.session.lnurlAuth.k1 || null;
    //if (!k1) {
    //  k1 = req.session.lnurlAuth.k1 = generateSecret(32, "hex");
    //  map.session.set(k1, req.session);
    //}

    k1 = generateSecret(32, "hex");

    const params = new URLSearchParams({
      k1,
      tag: "login"
    });

    const callbackUrl =`https://unlockd.gg/lapp/do-login?${params.toString()}`;
    console.log(callbackUrl);
    
    const encoded = lnurl.encode(callbackUrl).toUpperCase();
    const qrCode = await qrcode.toDataURL(encoded);

    try {
      const newChallenge = new lightningChallenge({k1: k1, bech_32_url: encoded})
      await newChallenge.save();
    } catch (error) {
      console.log(error.message);
      //next(error);
    }

    

    return res.json({
      lnurl: encoded,
      qrCode: qrCode,
    });
  }
  );


}

const generateSecret = function (numBytes, encoding) {
  numBytes = numBytes || 32;
  encoding = encoding || "hex";
  return crypto.randomBytes(numBytes).toString(encoding);
};

module.exports = { setupAuth: setupAuth };
