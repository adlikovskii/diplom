from django.urls import path

from .views import (
    CreateCustomUserViewSet,
    CreateContactView,
    UpdateCustomUserViewSet,
    GetContactView,
    ConfirmEmailView,
    UpdateContactView,
    DeleteContactView,
)

app_name = 'users'

urlpatterns = [
    # Регистрация нового пользователя
    path('registration/', CreateCustomUserViewSet.as_view(), name='registration'),

    # Добавление нового контакта
    path('add_contact/', CreateContactView.as_view(), name='add_contact'),

    # Обновление данных пользователя
    path('update_user/', UpdateCustomUserViewSet.as_view(), name='update_user'),

    # Получение списка контактов
    path('contacts/', GetContactView.as_view(), name='contacts'),

    # Подтверждение email с токеном
    path('confirm_email/<str:token>/<str:email>/', ConfirmEmailView.as_view(), name='confirm_email'),

    # Обновление конкретного контакта по ID
    path('update_contact/<int:pk>/', UpdateContactView.as_view(), name='update_contact'),

    # Удаление контакта по ID
    path('delete_contact/<int:pk>/', DeleteContactView.as_view(), name='delete_contact'),
]