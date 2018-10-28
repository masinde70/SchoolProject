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
#edit profile
path('edit/', views.edit, name='edit'),
#List
path('read_list/', views.AuctionListView.as_view(),  name="read_list"),
#confirm
path('create/auctions/new', views.AuctionConfirmView.as_view(), name='confirm'),
#edit
path('<int:auction_id>/edit', views.AuctionUpdateView.as_view(), name='auction_edit'),

#Detail
path('<int:pk>/',views.AuctionDetail.as_view(), name='auction-detail'),
#delete
path('<int:pk>/delete', views.AuctionDeleteView.as_view(), name='delete_auction'),
#read full
path('<int:auction_id>', views.AuctionReadView.as_view(), name='auction_read'),
path('confirm/',views.AuctionConfirmView, name='auction_confirm'),
# Bid for an auction
path('<int:auction_id>', views.BidCreateView.as_view(), name='bid_create'),

#api
path('api/', views.ApiAuctionListView.as_view()),
path('api/<int:pk>', views.AuctionDetail.as_view()),
path('apibid/', views.ApiBidCreateView.as_view())

]
