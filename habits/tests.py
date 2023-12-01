from django.db import connection
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        """
        Метод для установки тестовых данных.
        """
        self.client = APIClient()

        # Создание тестовых аккаунтов
        self.user = User.objects.create(
            email='member@test.ru',
            password='test',
            role='member',

            is_active=True,
        )
        # Аутентификация тестового аккаунта
        self.client.force_authenticate(user=self.user)
        self.user2 = User.objects.create(
            email='member2@test.ru',
            password='test',
            role='member',

            is_active=True,
        )

        # Создание тестовых привычек
        self.habit = Habit.objects.create(
            user=self.user,
            place="комнате",
            time_to_action='16:00:00',
            action="выпить стакан воды",
            is_pleasant_habit=False,
            related_habit=None,
            reward=None,
            is_publish=False
        )
        self.habit_1 = Habit.objects.create(
            user=self.user2,
            place="доме",
            time_to_action='16:00:00',
            action="отдохнуть от компьютера",
            is_pleasant_habit=False,
            related_habit=None,
            reward=None,
            is_publish=False
        )
        self.habit_3 = Habit.objects.create(
            user=self.user,
            place="спортзале",
            time_to_action='16:00:00',
            action="убрать спорт инвентарь на места",
            is_pleasant_habit=False,
            related_habit=None,
            reward=None,
            is_publish=True
        )
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="работе",
            time_to_action='16:00:00',
            action="сохранить все файлы перед окончанием рабочего дня",
            is_pleasant_habit=True,
            related_habit=None,
            reward=None,
            is_publish=False
        )

    def tearDown(self):
        """
        Метод срабатывающий после каждого теста и зачищающий тестовую базу данных.
        """

        # Удаляет всех пользователей и привычки
        User.objects.all().delete()
        Habit.objects.all().delete()
        super().tearDown()

        # Подключение к тесовой базе данных
        with connection.cursor() as cursor:
            # Сброс идентификаторов пользователей и привычек
            cursor.execute("""
                SELECT setval(pg_get_serial_sequence('"users_user"','id'), 1, false);
                SELECT setval(pg_get_serial_sequence('"habits_habit"','id'), 1, false);
            """)

    def test_get_habit_list(self):
        """
        Тест для получения списка полезных привычек.
        """

        response = self.client.get(
            reverse('habits:habit-list')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json()['count'],
            3
        )

        self.assertEqual(
            response.json()['results'][2],
            {'pk': 4, 'user': 1, 'place': 'работе', 'time_to_action': '16:00:00',
             'action': 'сохранить все файлы перед окончанием рабочего дня', 'is_pleasant_habit': True,
             'related_habit': None, 'periodicity': 'daily', 'reward': None, 'time_to_complete': '00:02:00',
             'is_publish': False}
        )

    def test_habit_retrieve(self):
        """
        Тест для получения существующей привычки.
        """

        response = self.client.get(
            reverse('habits:habit-detail', kwargs={'pk': self.habit.pk}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'pk': 1, 'user': 1, 'place': 'комнате', 'time_to_action': '16:00:00', 'action': 'выпить стакан воды',
             'is_pleasant_habit': False, 'related_habit': None, 'periodicity': 'daily', 'reward': None,
             'time_to_complete': '00:02:00', 'is_publish': False}
        )

    def test_another_habit_retrieve(self):
        """
        Тест для получения существующей привычки другого пользователя.
        """

        response = self.client.get(
            reverse('habits:habit-detail', kwargs={'pk': self.habit_1.pk}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_invalid_habit_retrieve(self):
        """
        Тест для получения существующей привычки.
        """

        response = self.client.get(
            reverse('habits:habit-detail', kwargs={'pk': 2}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_habit_create(self):
        """
        Тестирование создания привычки пользователем (валидными данными).
        """

        data = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "16:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": False,
        }

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Habit.objects.all().count(),
            5
        )

        self.assertTrue(
            response.json()['user'] == self.user.pk
        )

    def test_invalid_habit_create(self):
        """
        Тестирование создания привычки пользователем (невалидными данными).
        """

        data = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "17:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": 'Hello',
        }

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_related_or_reward_validator(self):
        """
        Тест валидатора CheckRelatedHabitOrReward,
        проверяющего, что нельзя выбрать одновременно вознаграждение и связанную привычку.
        """

        data = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "17:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": False,
            "related_habit": self.pleasant_habit.pk,
            "reward": 'Съешь конфетку',
        }

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Нельзя выбрать одновременно вознаграждение и связанную привычку.']}
        )

    def test_check_related_validator(self):
        """
        Тест валидатора CheckRelatedHabit,
        проверяющего, что в связанные привычки могут попадать только привычки с признаком приятной привычки.
        """

        data = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "18:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": False,
            "related_habit": self.habit.pk,
        }

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'non_field_errors': ['В связанные привычки могут попадать только привычки с признаком приятной привычки.']}
        )

    def test_check_pleasant_validator(self):
        """
        Тест валидатора CheckPleasantHabit,
        проверяющего, что у приятной привычки не может быть вознаграждения или связанной привычки.
        """

        data = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "19:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": True,
            "related_habit": self.pleasant_habit.pk,
        }
        data_1 = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "19:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": True,
            "reward": "Съешь конфетку"
        }

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'non_field_errors': ['У приятной привычки не может быть связанной привычки.']}
        )

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data_1
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'non_field_errors': ['У приятной привычки не может быть вознаграждения.']}
        )

    def test_check_time_validator(self):
        """
        Тест валидатора CheckTimeToComplete,
        проверяющего, что время выполнения должно быть не больше 120 секунд.
        """

        data = {
            "user": self.user.pk,
            "place": "шкафу",
            "time_to_action": "19:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": False,
            "time_to_complete": "00:05:00"
        }

        response = self.client.post(
            reverse('habits:habit-list'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'non_field_errors': [
                f'Время выполнения должно быть не больше 120 секунд. Ваше время {data["time_to_complete"]}'
            ]}
        )

    def test_habit_update(self):
        """
        Тестирование обновления привычки пользователем (валидными данными).
        """

        data = {
            "place": "шкафу",
            "time_to_action": "16:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": False,
        }

        response = self.client.put(
            reverse('habits:habit-detail', kwargs={'pk': self.habit.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'pk': 1, 'user': 1, 'place': 'шкафу', 'time_to_action': '16:00:00', 'action': 'разложить носки',
             'is_pleasant_habit': False, 'related_habit': None, 'periodicity': 'daily', 'reward': None,
             'time_to_complete': '00:02:00', 'is_publish': False}
        )

    def test_invalid_habit_update(self):
        """
        Тестирование обновления привычки пользователем (невалидными данными).
        """

        data = {
            "place": "шкафу",
            "time_to_action": "16:00:00",
            "is_pleasant_habit": False,
        }

        response = self.client.put(
            reverse('habits:habit-detail', kwargs={'pk': self.habit.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_another_habit_update(self):
        """
        Тестирование обновления привычки другого пользователя.
        """

        data = {
            "place": "шкафу",
            "time_to_action": "16:00:00",
            "action": "разложить носки",
            "is_pleasant_habit": False,
        }

        response = self.client.put(
            reverse('habits:habit-detail', kwargs={'pk': self.habit_1.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_habit_patch(self):
        """
        Тестирование частичного обновления привычки пользователем (валидными данными).
        """

        data = {
            "place": "шкафу",
        }

        response = self.client.patch(
            reverse('habits:habit-detail', kwargs={'pk': self.habit.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'pk': 1, 'user': 1, 'place': 'шкафу', 'time_to_action': '16:00:00', 'action': 'выпить стакан воды',
             'is_pleasant_habit': False, 'related_habit': None, 'periodicity': 'daily', 'reward': None,
             'time_to_complete': '00:02:00', 'is_publish': False}
        )

    def test_invalid_habit_patch(self):
        """
        Тестирование частичного обновления привычки пользователем (невалидными данными).
        """

        data = {
            "time_to_action": "шоколад",
        }

        response = self.client.patch(
            reverse('habits:habit-detail', kwargs={'pk': self.habit.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_another_habit_patch(self):
        """
        Тестирование частичного обновления привычки другого пользователя.
        """

        data = {
            "place": "шкафу",
        }

        response = self.client.patch(
            reverse('habits:habit-detail', kwargs={'pk': self.habit_1.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_habit_delete(self):
        """
        Тестирование удаления привычки пользователем (валидными данными).
        """

        response = self.client.delete(
            reverse('habits:habit-detail', kwargs={'pk': self.habit.pk}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            Habit.objects.all().count(),
            3
        )

    def test_invalid_habit_delete(self):
        """
        Тестирование удаления привычки пользователем (невалидными данными).
        """

        response = self.client.delete(
            reverse('habits:habit-detail', kwargs={'pk': 999}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_another_habit_delete(self):
        """
        Тестирование удаления привычки другого пользователя.
        """

        response = self.client.delete(
            reverse('habits:habit-detail', kwargs={'pk': self.habit_1.pk}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_publish_habit_list(self):
        """
        Тест на получение списка публичных привычек.
        """

        response = self.client.get(
            '/habit/publish/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            [{'pk': 3, 'user': 1, 'place': 'спортзале', 'time_to_action': '16:00:00',
              'action': 'убрать спорт инвентарь на места', 'is_pleasant_habit': False, 'related_habit': None,
              'periodicity': 'daily', 'reward': None, 'time_to_complete': '00:02:00', 'is_publish': True}]
        )

    def test_invalid_publish_habit_list(self):
        """
        Тест на получение списка публичных привычек (используя другой метод запроса).
        """

        response = self.client.post(
            '/habit/publish/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_publish_habit_detail(self):
        """
        Тест на получение деталей публичной привычки (передавая валидный идентификатор).
        """

        response = self.client.get(
            f'/habit/{self.habit_3.pk}/publish/detail/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'pk': 3, 'user': 1, 'place': 'спортзале', 'time_to_action': '16:00:00',
             'action': 'убрать спорт инвентарь на места', 'is_pleasant_habit': False, 'related_habit': None,
             'periodicity': 'daily', 'reward': None, 'time_to_complete': '00:02:00', 'is_publish': True}
        )

    def test_invalid_publish_habit_detail(self):
        """
        Тест на получение деталей публичной привычки (передавая невалидный идентификатор).
        """

        response = self.client.get(
            '/habit/999/publish/detail/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_invalid_publish_habit_post(self):
        """
        Тест на получение деталей публичной привычки (используя другой метод запроса).
        """

        response = self.client.post(
            f'/habit/{self.habit_3.pk}/publish/detail/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
