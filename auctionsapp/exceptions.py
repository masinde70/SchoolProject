'''
This file cannot be named exceptions.py as it already exists. Naming it exceptions.py leads to import exceptions.
'''

class BannedAuctionException(Exception):
    """Raised when an illegal action is taken on an auction in banned state"""


class DoneAuctionException(Exception):
    """Raised when an illegal action is taken on an auction in done state"""


class DueAuctionException(Exception):
    """Raised when an illegal action is taken on an auction in due state"""
