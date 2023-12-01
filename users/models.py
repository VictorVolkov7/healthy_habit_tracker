from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

NULLABLE = {'blank': True, 'null': True}


class UserRole(models.TextChoices):
    MEMBER = 'member', _('member')


class User(AbstractUser):
    """
    Класс для модели User.
    """

    username = None
    email = models.EmailField(unique=True, verbose_name='email')

    phone = models.CharField(max_length=35, verbose_name='номер телефона', **NULLABLE)
    country = models.CharField(max_length=50, verbose_name='страна', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)
    telegram = models.CharField(max_length=150, verbose_name='telegram', **NULLABLE)
    telegram_id = models.IntegerField(verbose_name='id пользователя telegram', **NULLABLE)

    role = models.CharField(max_length=15, verbose_name='роль', choices=UserRole.choices, default=UserRole.MEMBER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
