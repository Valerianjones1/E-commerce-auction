from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    auction_id = models.IntegerField(default=0)
    pass


class AuctionListingPage(models.Model):
    listing_name = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=64)
    url_image = models.CharField(
        max_length=200, default="https://image.shutterstock.com/image-vector/image-not-found-grayscale-photo-260nw-1737334631.jpg")
    starting_bid = models.FloatField()
    seller = models.CharField(max_length=64, default="Not Stated")
    closed = models.BooleanField(default=False)


class Bids(models.Model):
    auction_id = models.IntegerField()
    user_id = models.IntegerField(default=0)
    bid = models.FloatField()
    bid_date = models.CharField(max_length=100)


class Comments(models.Model):
    auction_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    comment_section = models.CharField(max_length=200)
    date = models.CharField(max_length=200, default="")


class Watchlist(models.Model):
    user_id = models.IntegerField()
    auc_id = models.IntegerField()
