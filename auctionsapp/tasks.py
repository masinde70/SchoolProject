
from django.core.mail import send_mail
from .models import Auction
from django.urls import reverse


def auction_created(auction, request):
    return (
        "Auction created",
        "Dear {username},\n\n"
        "Thank you for registering a new auction with us. We will get your item(s) sold in no time.\n"
        .format(
            username=request.user.username.capitalize()
        )
    )



def create_bid_email(bid, auction):
    return (
        "New Bid",
        "Dear All,\n\n"
        "A new bid of {amount:.2f} has been placed on auction '{title}'.\n\n"
        .format(
            amount=bid.amount,
            title=auction.title)
    )


def resolve_auction_email(auction):
    return (
        "Auction {title} concluded.".format(title=auction.title),
        "Dear All,\n\n"
        "The auction '{title}' has been resolved.\n\n"
            .format(
            title=auction.title,
        )
    )


def ban_auction_email(auction):
    return (
        "Auction {title} banned.".format(title=auction.title),
        "Dear All,\n\n"
        "The auction '{title}' has been banned.\n"
        "We apologize for any inconvenience.\n\n"
            .format(
            title=auction.title,
        )
    )
