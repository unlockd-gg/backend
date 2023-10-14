const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LightningWalletSchema = new Schema({
  session: {
    type: String,
    required: false
  },
  secret: {
    type: String,
    required: false
  },
  k1: {
    type: String,
    required: true
  },
  bech_32_url: {
    type: String,
    required: true
  },
  publickey: {
    type: String,
    required: false
  },
  userid: {
    type: String,
    required: false
  },
  userconnected: {
    type: Boolean,
    required: false
  },
  emailaddress: {
    type: String,
    required: false
  },
  emailverificationcode: {
    type: String,
    required: false
  },
  emailvalidated: {
    type: Boolean,
    required: false
  },
  fakewallet: {
    type: Boolean,
    required: false
  }
}, {
  timestamps: {
    createdAt: 'created', // Use `created` to store the created date
    updatedAt: 'updated' // and `updated` to store the last updated date
  }
});

const LightningWallet = mongoose.model('lightningwallets', LightningWalletSchema);
module.exports = LightningWallet;