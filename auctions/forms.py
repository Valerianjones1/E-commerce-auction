from django import forms


class AuctionListingForm(forms.Form):
    title = forms.CharField(label="Title:", max_length=64)
    category = forms.CharField(label="Category:", max_length=64)
    description = forms.CharField(widget=forms.Textarea, label="Description")
    starting_bid = forms.FloatField(label="Starting bid:")
    url_image = forms.URLField(max_length=100)
