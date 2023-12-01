from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Проверка, является пользователь владельцем объекта или нет.
    """

    message = 'Вы не являетесь владельцем.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsPublish(BasePermission):
    """
    Проверка, является привычка публичной или нет.
    """

    message = 'Данная привычка не является публичной.'

    def has_object_permission(self, request, view, obj):
        return obj.is_publish
