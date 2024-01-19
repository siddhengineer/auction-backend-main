from django.urls import include, path
from .views import ListingViewSet, BidView, ListingItemView, ListRetrieveView
from rest_framework.routers import SimpleRouter

listing_router = SimpleRouter()
listing_router.register("listing", ListingViewSet, basename="Listing View")

urlpatterns = [
    path("", include(listing_router.urls)),
    path("item/<int:pk>", ListRetrieveView.as_view(), name="Single Item View"),
    path("bid", BidView.as_view(), name="Bid View"),
]
