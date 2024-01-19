from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from auction.models import Bid, Item

from custom_auth.serializers import UserDetailSerializer, UserSerializer

from .models import User

# Create your views here.
class GoogleLoginView(APIView):
    def post(self, request):
        email = request.POST.data.get("email")
        user = User.objects.filter(email=email)
        if user.exists():
            refresh = RefreshToken(user.first())
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": f"User with emailId {email} does not exists."
            }, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    def post(self, request):
        try:
            data = request.data
            if User.objects.filter(username=data.get('username')).exists():
                return Response({
                    "error": "Username already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                username=data.get('username'),
                password=data.get("password")
            )
            user.email = data.get("email")
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                "refres h": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        try:
            if not getattr(request, "user"):
                return Response({
                    "error": "User not authenticated"
                }, status=status.HTTP_401_UNAUTHORIZED)
            return Response(UserDetailSerializer(request.user).data)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            if not getattr(request, "user"):
                return Response({
                    "error": "User not authenticated"
                }, status=status.HTTP_401_UNAUTHORIZED)
            user = UserSerializer(request.user, data=request.data)
            user = user.save()
            return Response(UserDetailSerializer(user).data)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, req):
        try:
            user = req.user
            data = []
            data['name'] = user.first_name + " " + user.last_name
            data['email'] = user.email
            data['username'] = user.username
            data['total_bids'] = Bid.objects.filter(user=user).count()
            data['auction_won'] = Bid.objects.filter(user=user, is_won=True).count()
            max_bid = Bid.objects.filter(user=user).order_by("-price")
            if max_bid.exists():
                data['max_bid'] = max_bid.first().price
            else:
                data['max_bid'] = 0
            data["total_items"] = Item.objects.filter(user=user).count()
            return Response(data)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

