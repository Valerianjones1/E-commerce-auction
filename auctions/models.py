from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListingPage(models.Model):
    listing_name = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=64)
    url_image = models.CharField(
        max_length=200, default="https://image.shutterstock.com/image-vector/image-not-found-grayscale-photo-260nw-1737334631.jpg")
    starting_bid = models.FloatField()


class Bids(models.Model):
    auction_id = models.IntegerField()
    bid = models.FloatField()
    bid_date = models.DateField()


class Comments(models.Model):
    comment_section = models.CharField(max_length=200)


class Watchlist(models.Model):
    user_id = models.IntegerField()
    auc_id = models.IntegerField()
