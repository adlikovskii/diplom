from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Админ-панель Django
    path("admin/", admin.site.urls),
    # API версии 1 — маршруты приложения пользователей
    path("api/v1/", include("users.urls")),
    # API версии 1 — маршруты backend-приложения с namespace
    path("api/v1/", include("backend.urls", namespace="backend")),
    # Аутентификация DRF (веб-интерфейс для входа/выхода)
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
]
