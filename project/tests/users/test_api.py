import pytest
from rest_framework.test import APIClient
import base64
from users.models import CustomUser, Contact


# Для корректной работы тестов в .env файле нужно заменить POSTGRES_HOST на 127.0.0.1


@pytest.fixture
def client():
    """
    Возвращает тестовый клиент API из Django REST Framework,
    который позволяет отправлять запросы к эндпоинтам.
    """
    return APIClient()


@pytest.fixture
def user():
    """
    Создаёт и возвращает пользователя с указанным email и паролем,
    который активен для тестовых целей.
    """
    user = CustomUser.objects.create_user(
        email="test_user@mail.ru", password="password", is_active=True
    )
    return user


@pytest.fixture
def contact(user):
    """
    Создаёт объект контакта с фиктивными данными,
    который связан с тестовым пользователем.
    """
    contact = Contact.objects.create(
        city="test",
        street="test",
        house="test",
        structure="test",
        building="test",
        apartment="test",
        phone="test",
        additional_desc="",
        user=user,
    )
    return contact


def encode_base64(string: str) -> str:
    """
    Кодирует строку в base64 для использования в HTTP заголовках авторизации.
    """
    return base64.b64encode(string.encode()).decode()


@pytest.mark.parametrize(
    ["email", "status_code"],
    (
        ("test_user@mail.ru", 201),  # правильный email — создаётся аккаунт
        ("test_user@mailru", 400),  # некорректный email — ошибка
    ),
)
@pytest.mark.django_db
def test_create_user(client, email, status_code):
    """
    Тестирует регистрацию нового пользователя.

    Проверяется:
    - корректность HTTP статуса,
    - при успешной регистрации аккаунт неактивен,
    - ответ содержит сообщение о необходимости подтверждения email.
    """
    response = client.post(
        "/api/v1/registration/",
        data={
            "email": email,
            "password": "secret",
        },
    )
    data = response.json()
    new_user = CustomUser.objects.filter(email="test_user@mail.ru").first()

    assert response.status_code == status_code
    if new_user:
        assert data == {
            "Success": "Account created successfully, please confirm your email"
        }
        assert new_user.is_active is False


@pytest.mark.django_db
def test_update_user(client, user):
    """
    Проверяет обновление данных пользователя.

    При смене email аккаунт деактивируется.
    При попытке повторной регистрации с новым email должна возвращаться ошибка.
    """
    response = client.patch(
        "/api/v1/update_user/",
        data={
            "email": "new_email@mail.ru",
            "password": "password",
        },
        headers={
            "Authorization": f'Basic {encode_base64("test_user@mail.ru:password")}',
            "Content-Type": "application/json",
        },
    )
    user.refresh_from_db()

    response_2 = client.post(
        "/api/v1/registration/",
        data={
            "email": "new_email@mail.ru",
            "password": "password",
        },
    )

    assert response.status_code == 201
    assert user.is_active is False
    assert response_2.status_code == 400


@pytest.mark.django_db
def test_create_contact(client, user):
    """
    Проверяет создание нового контакта, связанного с пользователем.
    """
    response = client.post(
        "/api/v1/add_contact/",
        data={
            "city": "test",
            "street": "test",
            "house": "test",
            "structure": "test",
            "building": "test",
            "apartment": "test",
            "phone": "test",
            "additional_desc": "",
        },
        headers={
            "Authorization": f'Basic {encode_base64("test_user@mail.ru:password")}',
            "Content-Type": "application/json",
        },
    )
    contact = Contact.objects.get(user=user.id)

    assert response.status_code == 201
    assert contact.user == user


@pytest.mark.django_db
def test_update_contact(client, user, contact):
    """
    Проверяет обновление данных существующего контакта.
    """
    response = client.put(
        f"/api/v1/update_contact/{contact.id}/",
        data={
            "city": "test1",
            "street": "test2",
            "house": "test3",
        },
        headers={
            "Authorization": f'Basic {encode_base64("test_user@mail.ru:password")}',
            "Content-Type": "application/json",
        },
    )
    contact.refresh_from_db()

    assert response.status_code == 200
    assert contact.city == "test1"
    assert contact.street == "test2"
    assert contact.house == "test3"
    # Поле structure не менялось, должно остаться прежним
    assert contact.structure == "test"


@pytest.mark.django_db
def test_get_contacts(client, user, contact):
    """
    Проверяет получение списка всех контактов пользователя.
    """
    response = client.get(
        "/api/v1/contacts/",
        headers={
            "Authorization": f'Basic {encode_base64("test_user@mail.ru:password")}',
            "Content-Type": "application/json",
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data[0].get("city") == "test"


@pytest.mark.django_db
def test_delete_contact(client, user, contact):
    """
    Проверяет удаление контакта пользователя.
    """
    response = client.delete(
        f"/api/v1/delete_contact/{contact.id}/",
        headers={
            "Authorization": f'Basic {encode_base64("test_user@mail.ru:password")}',
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 204
