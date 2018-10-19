from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import Http404
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.generic.edit import CreateView, FormMixin, DeleteView
from .models import Auction, Bid, Profile
from .serializers import AuctionSerializer
from auctionsapp.models import Auction
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError, transaction
from .forms import LoginForm, UserRegistrationForm, AuctionForm, UserEditForm, ProfileEditForm, BidForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from rest_framework import generics
from .exceptions import BannedAuctionException, DoneAuctionException, DueAuctionException
from .tasks import auction_created
from .permissions import IsAuthorOrReadOnly

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            return render(request,
                          'auctionsapp/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'auctionsapp/register.html',
                  {'user_form': user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile)
    return render(request,
                  'auctionsapp/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})

@login_required
def dashboard(request):
    return render(request,
                  'auctionsapp/dashboard.html',
                  {'section': 'dashboard'})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '
                                        'successfully')
                else:
                    return HttpResponse('Disabled auctionsapp')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'auctionsapp/login.html', {'form': form})

class AuctionCreateView(LoginRequiredMixin, CreateView):
    form_class = AuctionForm
    template_name = 'auctionsapp/create.html'

    def form_valid(self, form):
        for field in form.fields:
            form.fields[field].widget.attrs['readonly'] = True
        self.template_name = 'auctionsapp/confirm.html'
        return super(AuctionCreateView, self).form_invalid(form)

class AuctionConfirmView(AuctionCreateView):

    def get(self, request):
        raise Http404

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        email = auction_created(self.object, self.request)
        self.object.send_email(email[0], email[1], bidders=False)
        '''
        If we call super (ModelFormMixin) the form will be re-saved and self.object overwritten,
        have to call form_valid in FormMixin to avoid this issue.
        '''
        return FormMixin.form_valid(self, form)



class AuctionReadView(View):
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id)
        bids = auction.bid_set.all().order_by('-amount')
        response = render(
            request,
            'auctionsapp/read_full.html',
            {'auction': auction, 'bids': bids},
            content_type='text/html'
        )
        '''
        Store version number of fetched auction in a cookie
        so other views/operations can verify that the auction is not out of date.
        '''
        response.set_cookie('auction_version', auction.version)
        return response

class AuctionListView(ListView):
    queryset = Auction.objects.all()
    model = Auction
    template_name = 'auctionsapp/auction_list.html'
    content_type='text/html'


#Auction Delete View
class AuctionDeleteView(LoginRequiredMixin, DeleteView):
    model = Auction
    template_name = 'auctionsapp/delete.html'
    pk_url_kwarg = 'auction_id'


    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.

        Overrides delete() as defined in DeletionMixin. Make sure request belongs to author.
        """
        self.object = self.get_object()
        if self.object.author == self.request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot delete someone else's auction.")
            return HttpResponseRedirect(reverse('dashboard'))

    def get_success_url(self):
        return reverse('dashboard')


#api views
class ApiAuctionListView(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer


class AuctionDetail(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthorOrReadOnly,) #permission
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

#Bid create view
class BidCreateView(LoginRequiredMixin, View):
    model = Auction
    form_class = BidForm
    template_name = 'auctions/bid_create.html'
    content_type='text/html'
    pk_url_kwarg = 'auction_id'

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id)
        if not self.compare_versions(auction):
            return HttpResponseRedirect(reverse('auction_read', kwargs={'auction_id': auction_id}))
        form = BidForm()
        return render(
            request,
            self.template_name,
            {'form': form, 'auction_id': auction_id},
            content_type=self.content_type
        )
    
    def post(self, request, auction_id):
        from tasks import create_bid_email
        form = BidForm(request.POST or None)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {'form': form, 'auction_id': auction_id},
                content_type=self.content_type
            )
        amount = form.cleaned_data['amount']
        try:
            auction = None
            '''
            atomic insures no other user can insert a new bid after we have validated
            our bid as the greatest but before we have time to persist it.
            '''
            with transaction.atomic():
                auction = get_object_or_404(Auction, pk=auction_id)
                if not self.compare_versions(auction):
                    raise ValidationError("Has been edited")
                bid = auction.state.place_bid(request.user, amount) #try to place bid
            
            email = create_bid_email(bid, auction)
            auction.send_email(email[0], email[1])
        except IntegrityError:
            messages.add_message(request, messages.ERROR, "Your bid is too low. Outbid any previous bids and conform to the minimum bid.")
        except PermissionDenied:
            messages.add_message(request, messages.ERROR, "You may not bid on your own auction.")
        except DueAuctionException:
            messages.add_message(request, messages.ERROR, "Sorry, the deadline for this auction has passed.")
        except DoneAuctionException:
            messages.add_message(request, messages.ERROR, "Sorry, you may not bid on a concluded auction.")
        except BannedAuctionException:
            messages.add_message(request, messages.ERROR, "Sorry, you may not bid on a banned auction.")
            return HttpResponseRedirect(reverse('dashboard'))
        except ValidationError:
            '''
            Message is added by compare_versions()
            '''
            pass

        return HttpResponseRedirect(reverse('auction_read', kwargs={'auction_id': auction_id}))

    def compare_versions(self, auction):
        request_version = self.request.COOKIES.get('auction_version', 0)
        request_version = int(request_version)
        if auction.compare_version(request_version) != 0:
            messages.add_message(
                self.request,
                messages.ERROR,
                "We updated this auction for you. Please have a look at the changes before trying again."
            )
            return False
        return True


