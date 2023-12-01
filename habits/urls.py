from rest_framework.routers import DefaultRouter

from habits.api_views import HabitViewSet
from habits.apps import HabitsConfig

app_name = HabitsConfig.name

router = DefaultRouter()
router.register(r'habit', HabitViewSet, basename='habit')

urlpatterns = [
    # добавьте ваши дополнительные маршруты.
] + router.urls
