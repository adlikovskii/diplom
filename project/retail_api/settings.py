import os
from pathlib import Path
from dotenv import load_dotenv

# Формируем пути внутри проекта, например: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из .env файла
load_dotenv()

# ВАЖНО: храните секретный ключ в безопасности и не выкладывайте в публичные репозитории
SECRET_KEY = 'django-insecure-#zlbuo-@6(!s*1u--c0dg5=d*$&n@r5@d@q-xb-awbw!)fc0vb'

# Отключаем режим отладки в продакшене!
DEBUG = False

# Разрешённые хосты, которые могут обращаться к приложению
ALLOWED_HOSTS = [
    '*',  # В продакшене лучше указывать конкретные домены/хосты
]

# Пользовательская модель пользователя
AUTH_USER_MODEL = 'users.CustomUser'

# Бэкенды аутентификации (стандартный и кастомный для входа по email)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.EmailBackend',
]

# Установленные приложения проекта
INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения
    'rest_framework',
    'django_filters',

    # Собственные приложения
    'users',
    'backend',
]

# Middleware - цепочка обработки запросов и ответов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корневой конфиг урлов проекта
ROOT_URLCONF = 'diplom.urls'

# Настройка шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Путь к пользовательским директориям с шаблонами
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Добавляет request в контекст шаблонов
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Точка входа для WSGI
WSGI_APPLICATION = 'diplom.wsgi.application'


# Настройки базы данных PostgreSQL, с параметрами из переменных окружения
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'diplom'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'secret')
    }
}


# Валидация паролей (рекомендуется использовать в продакшене)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Настройки Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Настройки почтового сервера, значения берутся из .env
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
SERVER_EMAIL = os.getenv('SERVER_EMAIL')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Локализация и часовой пояс
LANGUAGE_CODE = 'ru-ru'  # Русский язык

TIME_ZONE = 'UTC'  # Часовой пояс UTC

USE_I18N = True  # Включить международализацию (переводы)

USE_TZ = True  # Использовать временные зоны


# Настройка статики (CSS, JS, изображения)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Тип поля по умолчанию для первичного ключа в моделях
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'