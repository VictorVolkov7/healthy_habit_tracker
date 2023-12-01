from rest_framework import serializers

from habits.models import Habit
from habits.validators import CheckRelatedHabitOrReward, CheckRelatedHabit, CheckPleasantHabit, CheckTimeToComplete, \
    CheckPeriodicity


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для модели Hebit.
    """

    class Meta:
        model = Habit
        fields = (
            'pk',
            'user',
            'place',
            'time_to_action',
            'action',
            'is_pleasant_habit',
            'related_habit',
            'periodicity',
            'reward',
            'time_to_complete',
            'is_publish'
        )
        validators = [
            CheckRelatedHabitOrReward(), CheckRelatedHabit(), CheckPleasantHabit(), CheckTimeToComplete(),
            CheckPeriodicity()
        ]


class CommonDetailSerializer(serializers.Serializer):
    """
    Сериалайзер для drf-spectacular документации.
    Показывает какие данные, выдает запрос при разных статусах.
    """
    detail = serializers.CharField()


class CommonDetailAndStatusSerializer(serializers.Serializer):
    """
    Сериалайзер для drf-spectacular документации.
    Показывает какие данные, выдает запрос при разных статусах.
    """
    status = serializers.IntegerField()
    details = serializers.CharField()
