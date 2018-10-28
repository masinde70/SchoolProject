from django.test import TestCase
from django.contrib.auth.models import User

from .models import Auction
# Create your tests here.

class AuctionTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        #create user
        testuser1 = User.objects.create_user(
            username='testuser1', email='testuser1@yahoo.com', password='abc123')
        testuser1.save()

        #create auction
        test_auction = Auction.objects.create(
            author=testuser1, title='Auction title', description='Auction content....', deadline='2018-11-26', min_price='11'
        )
        test_auction.save()
        test_auction.clean_fields()

    def test_auction_content(self):
        auction = Auction.objects.get(id=1)
        expected_author = f'{auction.author}'
        expected_title  = f'{auction.title}'
        expected_description = f'{auction.description}'
        self.assertEquals(expected_author, 'testuser1')
        self.assertEquals(expected_title, 'Auction title')
        self.assertEquals(expected_description, 'Auction content....')  

