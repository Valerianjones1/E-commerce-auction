from email.policy import default
from tabnanny import check
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
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


@login_required
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
        print(request.POST)
        form = BidForm(request.POST)
        comment_form = CommentForm(request.POST)
        auction_page = AuctionListingPage.objects.get(pk=auction_id)
        if form.is_valid():
            bid = float(form.cleaned_data["bid"])
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

                    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": BidForm(), "winner": ""})
            else:
                if float(bid) > auction_page.starting_bid:
                    bid_date = str(datetime.datetime.now()).split(".")[0]
                    bd = Bids(auction_id=auction_id, user_id=request.user.id,
                              bid=bid, bid_date=bid_date)
                    print(bd.bid)
                    bd.save()
                    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": BidForm(), "bid": bd, "winner": ""})
                else:
                    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": BidForm(), "winner": ""})
        elif comment_form.is_valid():
            comment = comment_form.cleaned_data["comments"]
            cmnts = Comments(auction_id=auction_id,
                             user_id=request.user.id, comment_section=comment, date=str(datetime.datetime.now()).split(".")[0])

            cmnts.save()
            try:
                comment = list(Comments.objects.filter(
                    auction_id=auction_id).filter(user_id=request.user.id))
            except Comments.DoesNotExist:
                comment = None
            try:
                user = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                user = None
            return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": form, "winner": "", "comment_form": CommentForm(), "user": user, "comment": comment[::-1]})
    else:
        try:
            watchlist = (Watchlist.objects.filter(
                auc_id=auction_id, user_id=request.user.id))
        except:
            watchlist = ""
        if len(watchlist) == 1:
            watchlist = True
        elif len(watchlist) == 0:
            watchlist = False

        else:
            watchlist = 1
            watchlist = True
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
            if active_list:
                active_list = check_length(active_list)
                winner_name = User.objects.get(pk=active_list.user_id)
                winner_name.auction_id = auction_id
                auction_page.closed = True
                auction_page.save()
                winner_name.save()
                return render(request, "auctions/listing_page.html", {"auction": auction_page, "watchlist": watchlist, "form": form, "comment": comment, "bid": bd, "winner": active_list, "comment_form": comment_form})
            else:
                # DO LOGIC WHEN OWNER OF ITEM WANTS TO CLOSE AUCTION WITHOUT ANY BIDS
                # DO SOME ALERT
                return render(request, "auctions/listing_page.html", {"auction": auction_page, "watchlist": watchlist, "form": form, "comment": comment, "bid": bd, "winner": "", "comment_form": comment_form})

    return render(request, "auctions/listing_page.html", {"auction": auction_page, "form": form, "watchlist": watchlist, "comment_form": comment_form, "bid": bd, "winner": "", "comment": comment[::-1]})


def show_watchlist(request):
    user_id = request.user.id
    if request.POST.get("watch"):
        auction_id = request.POST.get("watch")
        print(auction_id)
        wl = Watchlist(user_id=user_id, auc_id=auction_id)
        wl.save()
        bids = []
        items_l = []
        try:
            wl = list(Watchlist.objects.all())
        except Watchlist.DoesNotExist:
            wl = None
        if wl:
            for w in wl:
                if w.user_id == request.user.id:
                    try:
                        bds = check_length(
                            list(Bids.objects.filter(auction_id=w.auc_id)))
                    except Bids.DoesNotExist:
                        bds = None
                    auc_page = AuctionListingPage.objects.get(pk=w.auc_id)
                    items_l.append(auc_page)
                    bids.append(bds)
        return render(request, "auctions/watch_list.html", {"bids_item": zip(items_l, bids)})
    elif request.POST.get("unwatch"):
        bids = []
        items_l = []
        auction_id = request.POST.get("unwatch")
        wl = Watchlist.objects.get(auc_id=auction_id, user_id=user_id)
        wl.delete()
        watchlist = False
        try:
            wl = list(Watchlist.objects.all())
        except Watchlist.DoesNotExist:
            wl = None
        if wl:
            for w in wl:
                if w.user_id == request.user.id:
                    try:
                        bds = check_length(
                            list(Bids.objects.filter(auction_id=w.auc_id)))
                    except Bids.DoesNotExist:
                        bds = None
                    auc_page = AuctionListingPage.objects.get(pk=w.auc_id)
                    items_l.append(auc_page)
                    bids.append(bds)
        return render(request, "auctions/watch_list.html", {"bids_item": zip(items_l, bids), "watchlist": watchlist})
    else:
        bids = []
        items_l = []
        try:
            wl = list(Watchlist.objects.all())
        except Watchlist.DoesNotExist:
            wl = None
        if wl:
            for w in wl:
                if w.user_id == request.user.id:
                    try:
                        bds = check_length(
                            list(Bids.objects.filter(auction_id=w.auc_id)))
                    except Bids.DoesNotExist:
                        bds = None
                    auc_page = AuctionListingPage.objects.get(pk=w.auc_id)
                    items_l.append(auc_page)
                    bids.append(bds)
        return render(request, "auctions/watch_list.html", {"bids_item": zip(items_l, bids)})


def show_categories(request):
    auctions = list(AuctionListingPage.objects.all())
    categories = {}
    for auction in auctions:
        category = auction.category
        if category not in categories:
            categories[category] = []
            categories[category].append(auction)
        else:
            categories[category].append(auction)
    return render(request, "auctions/categories.html", {"categories": categories.items()})


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


# DO ALERTS FOR BIDS
# DO COMMENTS NAME IN MODE
# DO CATEGORIES
# DO CLOSE BID
# DO WATCH BUTTON AND CONDITIONS IN LAYOUT
