import datetime
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.serializers import ValidationError

from .models import Item, Bid


class ItemSerializer(ModelSerializer):
    owner_name = SerializerMethodField()
    def get_owner_name(self, obj):
        return obj.owner.username

    class Meta:
        model = Item
        fields = "__all__"

class BidSerializer(ModelSerializer):
    class Meta:
        model = Bid
        fields = "__all__"

    def validate(self, attrs):
        if attrs["price"] < attrs["item"].current_bid:
            raise ValidationError("Bid amount must be greater than current bid")

        return super().validate(attrs)

    def create(self, validated_data):
        bid = super().create(validated_data)
        bid.item.current_bid = bid.price
        bid.item.save()
        return bid


class BidderSerializer(ModelSerializer):
    bidder = SerializerMethodField()
    def get_bidder(self, obj):
        return [obj.user.username, obj.user.image]
    
    amount = SerializerMethodField()
    def get_amount(self, obj):
        return obj.price

    class Meta:
        model = Bid
        fields = ["bidder", "amount"]

class ListItemSerializer(ModelSerializer):
    bids = SerializerMethodField()
    start_date = SerializerMethodField()
    end_date = SerializerMethodField()
    start_time = SerializerMethodField()
    end_time = SerializerMethodField()
    owner_name = SerializerMethodField()
    
    def get_owner_name(self, obj):
        return obj.owner.username

    def get_start_date(self, obj):
        return obj.starting_time.strftime("%Y-%m-%d")
    
    def get_end_date(self, obj):
        return obj.ending_time.strftime("%Y-%m-%d")

    def get_start_time(self, obj):
        return obj.starting_time.strftime("%H:%M")
    
    def get_end_time(self, obj):
        return obj.ending_time.strftime("%H:%M")
    
    def get_bids(self,obj):
        try:
            res = BidderSerializer(Bid.objects.filter(item=obj).prefetch_related('user').order_by("-created"), many=True)
            return res.data
        except Exception as e:
            return []

    class Meta:
        model = Item
        fields = "__all__"