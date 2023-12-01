from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для модели User.
    """

    class Meta:
        model = User
        fields = ('email', 'password', 'phone', 'country', 'avatar', 'telegram',)

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        """
        Метод создания нового пользователя.
        """

        password = validated_data.pop('password', None)  # Достаем пароль из входных данных
        instance = User.objects.create(**validated_data)  # Создаем новый экземпляр пользователя
        if password is not None:
            instance.set_password(password)  # Устанавливаем хэшированный пароль
            instance.save()
            return instance


class TokenDetailAndStatusSerializer(serializers.Serializer):
    """
    Сериалайзер для drf-spectacular документации для токена.
    Показывает какие данные, выдает запрос при статусе 200.
    """
    refresh = serializers.CharField()
    access = serializers.CharField()


class TokenDetailSerializer(serializers.Serializer):
    """
    Сериалайзер для drf-spectacular документации для токена.
    Показывает какие данные, выдает запрос при статусе 200.
    """
    access = serializers.CharField()
