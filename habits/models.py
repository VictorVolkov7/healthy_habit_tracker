from datetime import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

NULLABLE = {'blank': True, 'null': True}


class HabitPeriodicity(models.TextChoices):
    """
    Модель с константами для выбора периодичности в модели Habit.
    """

    DAILY = 'daily', _('daily')
    MONDAY = 'monday', _('monday')
    TUESDAY = 'tuesday', _('tuesday')
    WEDNESDAY = 'wednesday', _('wednesday')
    THURSDAY = 'thursday', _('thursday')
    FRIDAY = 'friday', _('friday')
    SATURDAY = 'saturday', _('saturday')
    SUNDAY = 'sunday', _('sunday')


class Habit(models.Model):
    """
    Habit model.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        **NULLABLE,
        verbose_name='пользователь'
    )
    place = models.CharField(
        max_length=100,
        verbose_name='место выполнения'
    )
    time_to_action = models.TimeField(
        verbose_name='время, когда выполнять'
    )
    action = models.TextField(
        verbose_name='действие'
    )
    is_pleasant_habit = models.BooleanField(
        default=False,
        verbose_name='признак приятной привычки'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name='связанная привычка'
    )
    periodicity = models.CharField(
        max_length=9,
        choices=HabitPeriodicity.choices,
        default=HabitPeriodicity.DAILY,
        verbose_name='периодичность'
    )
    reward = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name='вознаграждение',
    )
    time_to_complete = models.TimeField(
        default=time(minute=2),
        verbose_name='время на выполнение'
    )
    is_publish = models.BooleanField(
        default=False,
        verbose_name='признак публичности'
    )

    def __str__(self):
        return f'{self.action} в {self.time_to_action} в {self.place}'

    class Meta:
        verbose_name = 'привычка'
        verbose_name_plural = 'привычки'
