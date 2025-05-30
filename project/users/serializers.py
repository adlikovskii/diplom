from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import CustomUser, Contact


class CreateCustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового пользователя.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'type', 'password']


class UpdateCustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления данных пользователя.
    При изменении email требуется повторное подтверждение.
    """
    email = serializers.EmailField(required=False, help_text='Изменение email требует повторного подтверждения аккаунта.')
    password = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'type', 'password']


class CreateContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания контактной информации.
    Пользователь заполняется автоматически.
    """
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'user', 'phone', 'additional_desc']


class UpdateContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления контактных данных.
    Все поля необязательны.
    """
    city = serializers.CharField(required=False, label='Город')
    street = serializers.CharField(required=False, label='Улица')
    phone = serializers.CharField(required=False, label='Телефон')
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'user', 'phone', 'additional_desc']


class GetContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения контактной информации.
    """
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'phone', 'additional_desc', 'user']