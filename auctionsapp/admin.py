from django.contrib import admin
from .models import Auction, Bid
'''
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    ordering = ('title')
    search_fields = ('title')
'''
# Register your models here.
admin.site.register(Auction)
admin.site.register(Bid)