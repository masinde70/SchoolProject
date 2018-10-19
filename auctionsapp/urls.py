from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path, include



urlpatterns = [
path('', include('django.contrib.auth.urls')),
path('', views.dashboard, name='dashboard'),
path('login/', auth_views.LoginView.as_view(), name='login'),
path('logout/', auth_views.LogoutView.as_view(), name='logout'),
# change password urls
path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
# reset password urls
path('password_reset/', auth_views.PasswordResetView.as_view(),name='password_reset'),
path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
path('register/', views.register, name='register'),
# create auction
path('create/', views.AuctionCreateView.as_view(), name='create'),
path('edit/', views.edit, name='edit'),
#List
path('Auction_list/', views.AuctionListView.as_view(),  name="Auction_list"),
#confirm
path('create/auctions/new', views.AuctionConfirmView.as_view(), name='confirm'),
#delete
path('<auction_id>\d+/delete$', views.AuctionDeleteView.as_view(), name='auction_delete'),
#read full
path('read_full/(?P<auction_id>\d+)$', views.AuctionReadView.as_view(), name='auction_read'),
path('confirm/',views.AuctionConfirmView, name='auction_confirm'),
# Bid for an auction
path('create_bid/(?P<auction_id>\d+)/bids/new', views.BidCreateView.as_view(), name='bid_create'),
#path('bid/', views.AuctionBid.as_view, name='Bid'),
#api
path('api/', views.ApiAuctionListView.as_view()),
path('api/<int:pk>', views.AuctionDetail.as_view()),
]
