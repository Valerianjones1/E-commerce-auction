from email.policy import default
from tabnanny import check
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
import datetime

from .models import AuctionListingPage, User,  Bids, Comments, Watchlist
from .forms import AuctionListingForm, BidForm, CommentForm


def index(request):
    active_list = list(AuctionListingPage.objects.all())
    actual_bids = []
    for line in list(active_list):
        bds = list(Bids.objects.filter(auction_id=line.id))
        if len(bds) > 1:
            bid = bds[-1].bid
            actual_bids.append(bid)
        elif len(bds) == 1:
            bid = bds[0].bid
            actual_bids.append(bid)

    if len(active_list) == len(actual_bids):
        return render(request, "auctions/index.html", {"active_list": zip(active_list, actual_bids)})
    else:
        return render(request, "auctions/index.html", {"active_list": zip(active_list, len(active_list)*[0])})


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
        if form.is_valid():
            title = form.cleaned_data["title"]
            category = form.cleaned_data["category"]
            description = form.cleaned_data.get("description")
            starting_bid = form.cleaned_data["starting_bid"]
            img_url = form.cleaned_data["url_image"]
            seller = request.user.username
            al = AuctionListingPage(listing_name=title, category=category,
                                    description=description, url_image=img_url, starting_bid=starting_bid, seller=seller)
            al.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = AuctionListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})


def listing_view(request, auction_id):
    if request.method == "POST":
        form = BidForm(request.POST)
        comment_form = CommentForm(request.POST)
        auction_page = AuctionListingPage.objects.get(pk=auction_id)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            try:
                bd_0 = list(Bids.objects.filter(auction_id=auction_id))
                bd_0 = check_length(bd_0)
            except Bids.DoesNotExist:
                bd_0 = 0
            if bd_0:
                if float(bid) > auction_page.starting_bid and float(bid) > bd_0.bid:
                    bid_date = str(datetime.datetime.now()).split(".")[0]
                    bd = Bids(auction_id=auction_id,
                              bid=bid, bid_date=bid_date, user_id=request.user.id)
                    print(bd.bid)
                    bd.save()
                    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": BidForm, "comment_form": CommentForm(), "bid": bd, "winner": ""})
                else:

                    return render(request, "auctions/listing_page.html", {"message":  "You can not bid lower than a starting price or current price!"})
            else:
                if float(bid) > auction_page.starting_bid:
                    bid_date = str(datetime.datetime.now()).split(".")[0]
                    bd = Bids(auction_id=auction_id, user_id=request.user.id,
                              bid=bid, bid_date=bid_date)
                    print(bd.bid)
                    bd.save()
                    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": BidForm(), "bid": bd, "winner": ""})
                else:
                    return HttpResponseRedirect(reverse("auctionpage"))
        elif comment_form.is_valid():
            comment = comment_form.cleaned_data["comments"]
            cmnts = Comments(auction_id=auction_id,
                             user_id=request.user.id, comment_section=comment)
            cmnts.save()
            try:
                comment = list(Comments.objects.filter(auction_id=auction_id))
            except Comments.DoesNotExist:
                comment = None
            return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": form, "winner": "", "comment_form": CommentForm(), "comment": comment})
    else:
        try:
            auction_page = AuctionListingPage.objects.get(pk=auction_id)
            bd = list(Bids.objects.filter(auction_id=auction_id))
        except Bids.DoesNotExist:
            bd = None
        form = BidForm()
        comment_form = CommentForm()
        bd = check_length(bd)

        try:
            comment = list(Comments.objects.filter(auction_id=auction_id))
        except Comments.DoesNotExist:
            comment = None
        if request.GET.get("close"):
            try:
                active_list = list(Bids.objects.filter(auction_id=auction_id))
            except Bids.DoesNotExist:
                active_list = ""
            active_list = check_length(active_list)
            winner_name = User.objects.get(pk=active_list.user_id)
            winner_name.auction_id = auction_id
            auction_page.closed = True
            auction_page.save()
            winner_name.save()
            return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": form, "comment": comment, "bid": bd, "winner": active_list, "comment_form": comment_form})

    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": form, "comment_form": comment_form, "bid": bd, "winner": "", "comment": comment})


def show_watchlist(request):
    user_id = request.user.id
    return render(request, "auctions/watch_list.html")


def check_length(array):
    if len(array) > 1:
        array = array[-1]
    elif len(array) == 1:
        array = array[0]
    return array

# def check_winner(request):
#     #user.id = user.id
#     if request.method == "POST":
#         # print(request.url)
#         auction_id = request.user.id
#         active_list = list(Bids.objects.get(auction_id=auction_id))
#         print(active_list)
#         return render(request, "auctions/listing_page.html", {"winner": active_list[-1]})
#     else:
#         return render(request, "auctions/listing_page.html", {"winner": ""})
