from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlist", views.create_listing, name="createlist"),
    path("auctionpage/<int:auction_id>", views.listing_view, name="auctionpage"),
    path("watchlist", views.show_watchlist, name="watchlist")
]
