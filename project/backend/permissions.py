from rest_framework.permissions import BasePermission


class IsOwnerOrderItem(BasePermission):
    """
    Разрешение на доступ только владельцу позиции заказа.
    """
    def has_object_permission(self, request, view, obj):
        # Проверка, принадлежит ли позиция заказа текущему пользователю
        return obj.order.user == request.user


class IsOwnerOrder(BasePermission):
    """
    Разрешение на доступ только владельцу заказа.
    """
    def has_object_permission(self, request, view, obj):
        # Проверка, принадлежит ли заказ текущему пользователю
        return obj.user == request.user