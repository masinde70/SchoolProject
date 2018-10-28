from django.db import models, IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, DecimalValidator
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from datetime import datetime
from django.core.mail import send_mail
from .exceptions import  BannedAuctionException, DueAuctionException, DoneAuctionException
from django.conf import settings



# Create your models here.
class Auction(models.Model):
    from auctionsapp.validators import validate_3_days_from_now
    STATE_BANNED = 0
    STATE_ACTIVE = 1
    STATE_DUE = 2
    STATE_DONE = 3
    '''
    Note that the order of choices matter. Each state most be in its corresponding index.
    '''
    STATE_CHOICES = (
        (STATE_BANNED, 'Banned'),
        (STATE_ACTIVE, 'Active'),
        (STATE_DUE, 'Due'),
        (STATE_DONE, 'Done'),
    )
    state = None

    class Meta:
        get_latest_by = "last_modified"

    title = models.CharField(max_length=250) #This is the field for the auction title. This field is CharField, which translates into a VARCHAR column in the SQL database.


    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_author') #This field is a foreign key. It defines a many-to-one relationship.
    # We are telling Django that each post is written by a user, and a user can write any number of posts
   
    created = models.DateTimeField(
        auto_now_add=True, #set to now upon creation
        editable=False,
        help_text="When auction was created"
    )

    deadline = models.DateField(
        help_text="Deadline for bids. Minimum of 3 days (dd/mm/yyyy).",
        validators=[validate_3_days_from_now]
    )

    description = models.TextField(
        max_length=1000,
        help_text="Precise description of item(s)"
    )

    min_price = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        help_text="Minimum amount accepted by seller",
        validators=[MinValueValidator(0.00)]
    )

    version = models.IntegerField(
        editable=False,
        default=0,
        help_text="Newest version"
    )

    bidders = models.ManyToManyField(
        User,
        through='Bid'
    )

    publish = models.DateTimeField(default=timezone.now) #This datetime indicates when the auction was published

    updated = models.DateTimeField(auto_now=True) #This datetime indicates the last time the auction was updated

    persisted_state = models.IntegerField(  #This field shows the status of a auction. I use a choices parameter, so the value of this field can only be set to one of the given choices
        editable=False,
        choices=STATE_CHOICES,
        default=STATE_ACTIVE,
        help_text="Current state of the auction"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auction_read', kwargs={'auction_id': self.pk})

    def is_author(self, user):
        return user == self.author

    def compare_version(self, version):
        """
        Compares the given version to the auctions version.
        Returns a negative integer for old version, zero for current version and positive integer for newer version.
        The value's magnitude corresponds to the difference in version.
        """
        return int(version) - self.version

    def send_email(self, title, message, author= True, bidders=True):
        recepients = []
        if author:
            author_email = self.author.email or None
            if author_email:
                recepients = [author_email]

            if bidders:

                '''
                Get list of bidder email addresses (removes duplicates).
                There are some edge cases to consider:
                No bidders will return an empty list. send_email() is okay with this (both if fail_silent=True/False)
                No email address results in an empty string entry. This element will have to be removed
                '''
            bidders_email = list(self.bidders.values_list('email', flat=True).exclude(email='').distinct())
            if bidders_email:
                recepients.extend(bidders_email)


        send_mail(
            title,
            message,
            'noreply@yaas.com',
            recepients,
            fail_silently=False,
        )


    def get_max_bid(self):
        '''
        Fetches the greatest bid placed on the auction
        The method is atomic.
        :return: Greatest bid
        '''
        bid_max = Bid.objects.filter(auction=self).aggregate(models.Max('amount'))  # this returns a dict
        return bid_max['amount__max']

    class State:

        def __init__(self, auction):
            self._auction = auction
            self._initialized = datetime.now()

        def place_bid(self, user, amount):
            """
            Base implementation of placing a bid on an auction. Creates and persists bid unconditionally.
            :param user: Bidding user
            :param amount: How much to bid
            :return: The saved Bid
            """
            if user == self._auction.author:
                raise PermissionDenied('Author may not bid on own auction')

            bid_max = Bid.objects.filter(auction=self._auction).aggregate(models.Max('amount'))  # this returns a dict
            bid_max = bid_max['amount__max']
            if bid_max is None:
                bid_max = self._auction.min_price
                if amount < bid_max:
                    raise IntegrityError("Bid must not be lower than lowest accepted amount")
            else:
                if amount <= bid_max:
                    raise IntegrityError("Bid must be greater than all existing bids")
            return Bid.objects.create(auction=self._auction, bidder=user, amount=amount)


class Bid(models.Model):
    class Meta:
        get_latest_by = 'last_modified'
        ordering = ['amount']

    auction = models.ForeignKey(
        'Auction',
        on_delete=models.CASCADE,
        help_text="Auction the bid was made on"
    )

    bidder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who placed the bid"
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        help_text="Amount bid",
        validators=[
            DecimalValidator(max_digits=20, decimal_places=2),
            MinValueValidator(0.01),
        ]
    )

    created = models.DateTimeField(
        auto_now_add=True, #set to now upon creation
        editable=False,
        help_text="When bid was placed"
    )

    last_modified = models.DateTimeField(
        auto_now=True, #sets date every time the object is saved
        editable=False,
        help_text="When bid was last updated"
    )

class ActiveState(Auction.State):
    """
    State for auction that is excepting bids
    """

class BannedState(Auction.State):
    """
    State for auction that has been banned by an admin.
    """

    def place_bid(self, user, amount):
        """
        :raises BannedAuctionException
        """
        state_name = Auction.STATE_CHOICES[Auction.STATE_BANNED][1].lower()
        raise BannedAuctionException(
            "User '{username}' tried to place a bid on {state_name} auction '{title}'"
            .format(
                username=user.username,
                state_name=state_name,
                title=self._auction.title
            )
        )

class DoneState(Auction.State):
    """
    State for auction that has been concluded.
    """

    def place_bid(self, user, amount):
        """
        :raises DoneAuctionException
        """
        state_name = Auction.STATE_CHOICES[Auction.STATE_DONE][1].lower()
        raise DoneAuctionException(
            "User '{username}' tried to place a bid on {state_name} auction '{title}'"
            .format(
                username=user.username,
                state_name=state_name,
                title=self._auction.title
            )
        )

class DueState(Auction.State):

    """
    State for auction which deadline has passed but that has yet to be concluded.
    """

    def place_bid(self, user, amount):
        """
        :raises DueAuctionException
        """
        '''
        #Soft deadline. Also requires that we set new deadline and update state
        if self._auction.deadline <= datetime.now() - datetime.timedelta(minutes=5):
            return super(DueState, self).place_bid(user, amount)
        '''
        state_name = Auction.STATE_CHOICES[Auction.STATE_DUE][1].lower()
        raise DueAuctionException(
            "User '{username}' tried to place a bid on {state_name} auction '{title}'"
            .format(
                username=user.username,
                state_name=state_name,
                title=self._auction.title
            )
        )

def restore_activity_state(**kwargs):
    auction = kwargs.get('instance')
    if auction.persisted_state == Auction.STATE_ACTIVE:
        auction.state = ActiveState(auction)
    elif auction.persisted_state == Auction.STATE_DONE:
        auction.state = DoneState(auction)
    elif auction.persisted_state == Auction.STATE_DUE:
        auction.state = DueState(auction)
    elif auction.persisted_state == Auction.STATE_BANNED:
        auction.state = BannedState(auction)
    else:
        auction.state = ActiveState(auction)   #fallback
    return auction.state

    models.signals.post_init.connect(restore_activity_state, Auction)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)
