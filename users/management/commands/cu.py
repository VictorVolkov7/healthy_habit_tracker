from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='test1@mail.ru',

            is_active=True
        )

        user.set_password('qwe123')
        user.save()
