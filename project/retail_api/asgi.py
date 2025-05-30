"""
ASGI конфигурация для проекта diplom.

Этот модуль предоставляет ASGI-приложение в виде переменной верхнего уровня с именем ``application``.

Подробности можно найти по ссылке:
https://docs.djangoproject.com/ru/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Устанавливаем переменную окружения с настройками Django по умолчанию для ASGI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diplom.settings")

# Получаем экземпляр ASGI-приложения
application = get_asgi_application()
