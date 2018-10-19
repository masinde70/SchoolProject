from django.contrib import admin
from .models import Auction, Bid, Profile
'''
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    ordering = ('title')
    search_fields = ('title')
'''
# Register your models here.
admin.site.register(Auction)
admin.site.register(Bid)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']
