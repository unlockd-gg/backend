import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class GroupRaidMembers(ndb.Model):
    groupKeyId = ndb.IntegerProperty()
    groupTitle = ndb.StringProperty()

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty()

    teamKeyId = ndb.IntegerProperty()
    teamTitle = ndb.StringProperty()

    captainKeyId = ndb.IntegerProperty()
    captainTitle = ndb.StringProperty()

    groupRaidKeyId = ndb.IntegerProperty() # current raid
    groupRaidTitle = ndb.StringProperty() # current raid

    userKeyId = ndb.IntegerProperty()
    userTitle = ndb.StringProperty()

    vettingEnabled = ndb.BooleanProperty()
    vettingCompleted = ndb.BooleanProperty()
    vettingFinalized = ndb.BooleanProperty()

    raidActive = ndb.BooleanProperty()
    ## TODO add more group permissions

    gkpAmount = ndb.FloatProperty()
    gkpAmountSpentThisRaid = ndb.FloatProperty()
    gkpVettingThisRaid = ndb.FloatProperty()
    gkpVettingRemaining = ndb.IntegerProperty()

    startedTime = ndb.DateTimeProperty()
    completedTime = ndb.DateTimeProperty()
    finalizedTime = ndb.DateTimeProperty()

    def to_json(self):
        #now = datetime.datetime.now()
        return ({
                u'key_id': str(self.key.id()),
                u'userKeyId': self.userKeyId,
                u'userTitle': self.userTitle,
                #u'userAvatarTheme': self.userAvatarTheme,
                u'gkpAmount': self.gkpAmount,
                u'gkpVettingThisRaid': self.gkpVettingThisRaid,
                u'gkpVettingRemaining': self.gkpVettingRemaining
        })
