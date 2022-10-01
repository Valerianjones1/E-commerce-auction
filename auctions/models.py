from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    listing_name = models.CharField(max_length=64, primary_key=True)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=64)
    url_image = models.CharField(
        max_length=200, default="https://image.shutterstock.com/image-vector/image-not-found-grayscale-photo-260nw-1737334631.jpg")
    starting_bid = models.FloatField()


class AuctionListingPage(models.Model):
    listing_name = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=64)
    url_image = models.CharField(
        max_length=200, default="https://image.shutterstock.com/image-vector/image-not-found-grayscale-photo-260nw-1737334631.jpg")
    starting_bid = models.FloatField()


class Bids(models.Model):
    bid = models.FloatField()
    bid_date = models.DateField()


class Comments(models.Model):
    comment_section = models.CharField(max_length=200)
