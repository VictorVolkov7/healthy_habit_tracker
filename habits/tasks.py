import requests
from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from habits.models import Habit
from users.models import User

WEEKDAY = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday',
}


@shared_task
def get_telegram_user_id():
    """
    Периодическая задача для просмотра логов бота, чтобы достать id пользователя по его username.
    """

    # получаем всех пользователей, которые указали свой телеграм
    for user in User.objects.filter(~Q(telegram=None)):
        # обращаемся к логам и получаем id
        response = requests.get(f'{settings.TG_URL}/bot{settings.TG_BOT_API}/getUpdates').json()
        desired_user_id = next((item["message"]["from"]["id"] for item in response["result"] if
                                item["message"]["from"]["username"] == user.telegram), None)

        # присваиваем id пользователю
        if desired_user_id:
            user.telegram_id = desired_user_id
            user.save()


@shared_task
def telegram_integration():
    """
    Периодическая задача для отправки уведомления о привычки в telegram.
    """
    # Получение дня недели и времени текущего часового пояса
    datetime = timezone.datetime.now()
    weekday = datetime.date().weekday()
    time = datetime.time().strftime('%H:%M')

    # Получение привычек по заданным параметрам
    habits = Habit.objects.filter(time_to_action=time, periodicity__in=[WEEKDAY[weekday], 'daily'])

    if habits:
        for habit in habits:
            if habit.user.telegram_id:
                params = {
                    'chat_id': habit.user.telegram_id,
                    'text': habit
                }
                requests.post(f'{settings.TG_URL}/bot{settings.TG_BOT_API}/sendMessage', params=params)
