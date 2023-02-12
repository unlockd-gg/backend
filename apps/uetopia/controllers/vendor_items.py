from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.uetopia.models.vendor_items import VendorItems

class VendorItemsController(BaseController):
    """Vendor Items Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = VendorItems

    def get_by_vendorKeyId(self, vendorKeyId):
        """ get all for a vendorKeyId """
        query = self.model.query()
        query = query.filter(self.model.vendorKeyId == vendorKeyId)
        return query.fetch(1000)

    def get_selling_by_vendorKeyId(self, vendorKeyId):
        """ get all for a serverKey """
        query = self.model.query()
        query = query.filter(self.model.vendorKeyId == vendorKeyId)
        query = query.filter(self.model.selling == True)
        return query.fetch(1000)

    def get_buyingOffer_by_vendorKeyId(self, vendorKeyId):
        """ get all for a serverKey """
        query = self.model.query()
        query = query.filter(self.model.vendorKeyId == vendorKeyId)
        query = query.filter(self.model.buyingOffer == True)
        return query.fetch(1000)

    def get_claimableAsCurrency_by_vendorKeyId_claimableForUserKeyId(self, vendorKeyId, claimableForUserKeyId):
        """ get claimable for a user on a vendor """
        query = self.model.query()
        query = query.filter(self.model.vendorKeyId == vendorKeyId)
        query = query.filter(self.model.claimableForUserKeyId == claimableForUserKeyId)
        query = query.filter(self.model.claimableAsCurrency == True)
        return query.fetch(1000)

    def get_claimableAsItem_by_vendorKeyId_claimableForUserKeyId(self, vendorKeyId, claimableForUserKeyId):
        """ get claimable for a user on a vendor """
        query = self.model.query()
        query = query.filter(self.model.vendorKeyId == vendorKeyId)
        query = query.filter(self.model.claimableForUserKeyId == claimableForUserKeyId)
        query = query.filter(self.model.claimableAsItem == True)
        return query.fetch(1000)
