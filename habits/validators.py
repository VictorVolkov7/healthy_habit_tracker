from datetime import time

from rest_framework.serializers import ValidationError

from habits.models import Habit


class CheckRelatedHabitOrReward:
    """
    Проверка, что нельзя выбрать одновременно вознаграждение и связанную привычку.
    """

    def __call__(self, data):
        related_habit = data.get('related_habit')
        reward = data.get('reward')

        if related_habit and reward:
            raise ValidationError('Нельзя выбрать одновременно вознаграждение и связанную привычку.')


class CheckRelatedHabit:
    """
    Проверка, что в связанные привычки могут попадать только привычки с признаком приятной привычки.
    """

    def __call__(self, data):
        related_habit = data.get('related_habit')
        if related_habit:
            habit = Habit.objects.get(pk=related_habit.pk)
            if not habit.is_pleasant_habit:
                raise ValidationError(
                    'В связанные привычки могут попадать только привычки с признаком приятной привычки.'
                )


class CheckPleasantHabit:
    """
    Проверка, что у приятной привычки не может быть вознаграждения или связанной привычки.
    """

    def __call__(self, data):
        is_pleasant_habit = data.get('is_pleasant_habit')
        related_habit = data.get('related_habit')
        reward = data.get('reward')

        if is_pleasant_habit and related_habit:
            raise ValidationError('У приятной привычки не может быть связанной привычки.')
        elif is_pleasant_habit and reward:
            raise ValidationError('У приятной привычки не может быть вознаграждения.')


class CheckTimeToComplete:
    """
    Проверка, что время выполнения должно быть не больше 120 секунд.
    """

    def __call__(self, data):
        time_to_complete = data.get('time_to_complete')

        if time_to_complete is not None and time_to_complete > time(minute=2):
            raise ValidationError(
                f'Время выполнения должно быть не больше 120 секунд. Ваше время {time_to_complete}'
            )


class CheckPeriodicity:
    """
    Проверка, что пользователь выберет периодичность не реже, чем 1 раз в 7 дней.
    """

    def __call__(self, data):
        periodicity = data.get('periodicity')

        if periodicity is not None and not periodicity:
            raise ValidationError('Нельзя выполнять привычку реже, чем 1 раз в 7 дней.')
