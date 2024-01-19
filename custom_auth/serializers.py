from rest_framework import serializers
from django.contrib.auth import get_user_model

from auction.models import Bid, Item

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    auction_won = serializers.SerializerMethodField()
    max_bid = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj.first_name) + " " + str(obj.last_name)

    def get_total_bids(self, obj):
        qs = Bid.objects.filter(user=obj).count()
        return qs

    def get_auction_won(self, obj):
        qs = Bid.objects.filter(user=obj, is_won=True).count()
        return qs

    def get_max_bid(self, obj):
        qs = Bid.objects.filter(user=obj).order_by("-price")
        if qs.exists():
            return qs.first().price
        return 0
    
    def get_total_items(self, obj):
        qs = Item.objects.filter(owner=obj).count()
        return qs

    class Meta:
        model = User
        fields = "__all__"


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        required = ("username",)

    def validate(self, attrs):
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists")
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
