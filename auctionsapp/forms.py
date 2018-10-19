from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput
from django.contrib.auth.models import User
from auctionsapp.models import Auction, Bid, Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')
        
class AuctionForm(ModelForm):
    confirmed = BooleanField(
        required=False,
        initial=False,
        help_text='whether the form has been confirmed',
        widget=HiddenInput
    )

    class Meta:
        model = Auction
        fields = ["title", "description", "min_price", "deadline",]

    # This method might be superfluous if the form in auction creation has it's author set directly
    def save(self, commit=True, *args, **kwargs):
        user = kwargs.pop('user') if 'user' in kwargs else None  # Pop is important as super does not recognize user keyword
        auction = super(AuctionForm, self).save(commit=False, *args, **kwargs)
        if getattr(auction, 'author', None) is None and user is not None:
            auction.author = user
        if commit:
            auction.save()
        return auction



class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
