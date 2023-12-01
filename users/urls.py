from django.urls import path

from users.api_views import UserCreateAPIView, TokenObtainPairView, TokenRefreshView
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
]
