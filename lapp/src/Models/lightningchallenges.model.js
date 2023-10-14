const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LightningChallengeSchema = new Schema({
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
  }
}, {
  timestamps: {
    createdAt: 'created', // Use `created` to store the created date
    updatedAt: 'updated' // and `updated` to store the last updated date
  }
});

const LightningChallenge = mongoose.model('lightningchallenges', LightningChallengeSchema);
module.exports = LightningChallenge;