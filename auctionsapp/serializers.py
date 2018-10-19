from rest_framework import serializers
from .models import Auction

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'description',
            'deadline',
            'min_price',
            'persisted_state',
            'version',
            'author',
            'created', 
        )
       