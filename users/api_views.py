from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from habits.serializers import CommonDetailSerializer, CommonDetailAndStatusSerializer
from users.serializers import TokenDetailAndStatusSerializer, TokenDetailSerializer
from users.serializers import UserSerializer


@extend_schema(
    summary="Регистрация нового пользователя.",
    responses={
        status.HTTP_201_CREATED: UserSerializer,
        status.HTTP_400_BAD_REQUEST: CommonDetailSerializer,
        status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
        status.HTTP_403_FORBIDDEN: CommonDetailAndStatusSerializer,
        status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
    }
)
class UserCreateAPIView(generics.CreateAPIView):
    """
    Контроллер для создания пользователя.
    """

    serializer_class = UserSerializer


@extend_schema(
    summary="Используется для запроса пары токенов (access и refresh).",
    responses={
        status.HTTP_200_OK: TokenDetailAndStatusSerializer,
        status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
        status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
        status.HTTP_405_METHOD_NOT_ALLOWED: CommonDetailSerializer,
    }
)
class TokenObtainPairView(BaseTokenObtainPairView):
    pass


@extend_schema(
    summary="Используется для обновления access-токена при истечении его срока действия.",
    responses={
        status.HTTP_200_OK: TokenDetailSerializer,
        status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
        status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
        status.HTTP_405_METHOD_NOT_ALLOWED: CommonDetailSerializer,
    }
)
class TokenRefreshView(BaseTokenRefreshView):
    pass
