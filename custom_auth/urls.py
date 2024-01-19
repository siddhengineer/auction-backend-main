from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from .views import UserView

urlpatterns = [
    path(
        "token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "user/", UserView.as_view(), name="UserView"
    ),
    path(
        "user/<int:userId>", UserView.as_view(), name="UserView"
    )
]
