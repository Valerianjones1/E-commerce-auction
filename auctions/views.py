from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import AuctionListingPage, User,  Bids, Comments
from .forms import AuctionListingForm, BidForm


def index(request):
    active_list = AuctionListingPage.objects.all()

    print(active_list)
    return render(request, "auctions/index.html", {"active_list": active_list})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        print(form)
        if form.is_valid():
            title = form.cleaned_data["title"]
            category = form.cleaned_data["category"]
            description = form.cleaned_data.get("description")
            starting_bid = form.cleaned_data["starting_bid"]
            img_url = form.cleaned_data["url_image"]
            al = AuctionListingPage(listing_name=title, category=category,
                                    description=description, url_image=img_url, starting_bid=starting_bid)
            al.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = AuctionListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})


def listing_view(request, auction_id):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            bid_date = str(datetime.datetime.now()).split(".")[0]
            bd = Bids(auction_id=auction_id, bid=bid, bid_date=bid_date)
            bd.save()

    else:
        auction_page = AuctionListingPage.objects.get(pk=auction_id)
        form = BidForm()
        print(auction_page.id)
    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": form})


def show_watchlist(request):
    user_id = request.user.id
