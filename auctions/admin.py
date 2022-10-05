from django.contrib import admin
from .models import User, Bids, Comments, AuctionListingPage
# Register your models here.

admin.site.register(User)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(AuctionListingPage)
