from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit
from habits.paginators import MyPaginator
from habits.permissions import IsOwner, IsPublish
from habits.serializers import HabitSerializer, CommonDetailSerializer, CommonDetailAndStatusSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Получить список привычек.",
        responses={
            status.HTTP_200_OK: HabitSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
            status.HTTP_405_METHOD_NOT_ALLOWED: CommonDetailSerializer,
        }
    ),
    retrieve=extend_schema(
        summary="Получить существующую привычку по ее идентификатору.",
        responses={
            status.HTTP_200_OK: HabitSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
            status.HTTP_405_METHOD_NOT_ALLOWED: CommonDetailSerializer,
        }
    ),
    update=extend_schema(
        summary="Изменение существующей привычки.",
        responses={
            status.HTTP_200_OK: HabitSerializer,
            status.HTTP_400_BAD_REQUEST: CommonDetailSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
        }
    ),
    partial_update=extend_schema(
        summary="Частичное изменение существующей привычки.",
        responses={
            status.HTTP_200_OK: HabitSerializer,
            status.HTTP_400_BAD_REQUEST: CommonDetailSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_403_FORBIDDEN: CommonDetailAndStatusSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
        }
    ),
    create=extend_schema(
        summary="Создание новой привычки.",
        responses={
            status.HTTP_201_CREATED: HabitSerializer,
            status.HTTP_400_BAD_REQUEST: CommonDetailSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_403_FORBIDDEN: CommonDetailAndStatusSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
        }
    ),
    destroy=extend_schema(
        summary="Удаление существующей привычки.",
        responses={
            status.HTTP_204_NO_CONTENT: '',
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_403_FORBIDDEN: CommonDetailAndStatusSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
        }
    ),
)
class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = MyPaginator

    def perform_create(self, serializer):
        habit = serializer.save()
        habit.user = self.request.user
        habit.save()

    def get_queryset(self):
        """
        Получение queryset, в зависимости от запроса пользователя.
        Если в запросе присутствует publish, то выбирается queryset с фильтрацией по признаку публичности.
        Во всех остальных случаях выбирается queryset с фильтрацией по текущему пользователю.
        """

        if 'publish' in self.request.path:
            return Habit.objects.filter(is_publish=True)
        else:
            return Habit.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsOwner | IsPublish]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Получить список публичных привычек.",
        responses={
            status.HTTP_200_OK: HabitSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
            status.HTTP_405_METHOD_NOT_ALLOWED: CommonDetailSerializer,
        }
    )
    @action(
        methods=['get'],
        detail=False,
        url_path='publish',
        url_name='publish_list'
    )
    def publish_habits_list(self, request):
        """
        Логика для обработки запроса habit/publish/. Чтобы пользователи могли видеть публичные привычки.
        """
        serializer = self.get_serializer(self.get_queryset(), many=True)

        if serializer.is_valid:
            return Response(serializer.data)
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Получить детали публичной привычки по её идентификатору.",
        responses={
            status.HTTP_200_OK: HabitSerializer,
            status.HTTP_401_UNAUTHORIZED: CommonDetailSerializer,
            status.HTTP_404_NOT_FOUND: CommonDetailSerializer,
            status.HTTP_405_METHOD_NOT_ALLOWED: CommonDetailSerializer,
        },
    )
    @action(
        methods=['get'],
        detail=True,
        url_path='publish/detail',
        url_name='publish_detail',
        permission_classes=[IsAuthenticated, IsPublish]
    )
    def retrieve_publish_habit(self, request, pk: int = None):
        """
        Логика для обработки запроса habit/<int:pk>/publish/. Чтобы пользователи могли видеть детали публичных привычек.
        """

        habit = self.get_object()
        serializer = self.get_serializer(habit)

        if serializer.is_valid:
            return Response(serializer.data)
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
