"""
WSGI-конфигурация для проекта dpilom.

Этот файл предоставляет переменную модуля ``application``,
которая используется сервером WSGI для запуска проекта.

Подробнее можно узнать в документации:
https://docs.djangoproject.com/ru/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Устанавливаем переменную окружения с настройками Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diplom.settings')

# Получаем объект WSGI-приложения для сервера
application = get_wsgi_application()