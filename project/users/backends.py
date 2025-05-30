from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Аутентификация пользователя по email и паролю.

        Аргументы:
            request (HttpRequest): объект запроса.
            username (str): email пользователя.
            password (str): пароль пользователя.
            **kwargs: дополнительные параметры.

        Возвращает:
            Пользователь (User), если аутентификация успешна, иначе None.
        """
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
