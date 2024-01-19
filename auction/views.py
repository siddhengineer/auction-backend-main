from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from auction.serializers import BidSerializer, ItemSerializer, ListItemSerializer
from .models import Item, Bid
from datetime import datetime
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
import logging
# Create your views here.

logger = logging.getLogger(__name__)

class ListingViewSet(
    ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        q_type = self.request.GET.get("type", "none")
        logging.info(q_type)
        day = datetime.now()
        qs = self.queryset
        if "live" in q_type:
            qs = Item.objects.filter(
                starting_time__lte=day,
                ending_time__gte=day,
            )
        elif q_type == "upcoming":
            qs = Item.objects.filter(
                starting_time__gte=day
            )
        elif q_type == "past":
            qs = Item.objects.filter(
                ending_time__lte=day
            )
        elif q_type == "personal":
            qs = Item.objects.filter(owner=self.request.user)
        else:
            qs = Item.objects.all()
        qs = qs.prefetch_related("owner")
        print(qs)
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ListItemSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data["owner"] = request.user.pk
            strt_date = data['start_date'] + " " + data['start_time']
            end_date = data['end_date'] + " " + data['end_time']
            data['starting_time'] = datetime.strptime(strt_date, "%Y-%m-%d %H:%M")
            data['ending_time'] = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            item = ItemSerializer(data=data)
            item.is_valid(raise_exception=True)
            item = item.save()
            return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

class ListingItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q_type = request.GET.get("type", "live")
        today = datetime.now().today()
        now = datetime.now().time()
        if q_type == "live":
            qs = Item.objects.filter(
                start_date__lte=today,
                start_time__lte=now,
                end_date__gt=today,
                end_time__gt=now,
            )
        elif q_type == "upcoming":
            qs = Item.objects.filter(
                Q(start_date__gt=today) | Q(start_date=today, start_time__gte=now)
            )
        elif q_type == "past":
            qs = Item.objects.filter(
                Q(end_date__lt=today) | Q(end_date=today, end_time__lt=now)
            )
        elif q_type == "personal":
            qs = Item.objects.filter(owner=request.user)
        else:
            qs = Item.objects.all()
        qs = qs.prefetch_related("owner")
        return Response(ItemSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            data = request.data
            data["owner"] = request.user.pk
            item = ItemSerializer(data=data)
            item.is_valid(raise_exception=True)
            item = item.save()
            return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class BidView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pass

    def post(self, request):
        data = request.data
        try:
            data['user'] = request.user.pk
            serializer = BidSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListRetrieveView(APIView):
    def get(self, req, pk):
        # try:
            item = Item.objects.get(pk=pk)
            return Response(ListItemSerializer(item).data, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response(status=404)
