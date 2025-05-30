from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его владельцу.
    Другие пользователи имеют только права на чтение.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить доступ, если текущий пользователь — владелец объекта
        return obj.user == request.user
