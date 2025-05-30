from django.apps import AppConfig


class UsersConfig(AppConfig):
    # Устанавливаем тип автоинкрементного поля по умолчанию для моделей
    default_auto_field = "django.db.models.BigAutoField"
    # Имя приложения
    name = "users"
