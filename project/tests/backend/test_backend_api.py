import pytest
from rest_framework.test import APIClient
import base64

from backend.models import Shop, Product, ProductInfo, Order, OrderItem
from users.models import CustomUser, Contact


@pytest.fixture
def client():
    """
    Фикстура, возвращающая клиент для тестирования API на базе
    rest_framework.test.APIClient, который используется для имитации запросов к серверу.
    """
    return APIClient()


@pytest.fixture
def user():
    """
    Создаёт и возвращает тестового пользователя с указанной почтой и паролем,
    активного и с типом 'shop' для тестирования.
    """
    user = CustomUser.objects.create_user(
        email='test_user@mail.ru',
        password='password',
        is_active=True,
        type='shop'
    )
    return user


@pytest.fixture
def contact(user):
    """
    Создаёт тестовый контакт, связанный с пользователем `user`,
    с фиктивными данными адреса и телефона.
    """
    contact = Contact.objects.create(
        city='test',
        street='test',
        house='test',
        structure='test',
        building='test',
        apartment='test',
        phone='test',
        additional_desc='',
        user=user
    )
    return contact


@pytest.fixture
def products(client):
    """
    Загружает данные товаров из внешнего YAML-файла по URL и
    возвращает все объекты Product из базы.
    """
    response = client.post('/api/v1/upload/', data={
        'url': 'https://raw.githubusercontent.com/adlikovskii/diplom/refs/heads/main/shop1.yaml',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
        'Content-Type': 'application/json'
    })
    products = Product.objects.all()
    return products


def encode_base64(string: str) -> str:
    """
    Преобразует строку в base64 для использования в HTTP Basic Auth заголовках.

    Args:
        string (str): Строка с данными для кодирования (например, 'email:password').

    Returns:
        str: Результат кодирования в base64 в виде строки.
    """
    return base64.b64encode(string.encode()).decode()


@pytest.mark.parametrize(
    ['quantity', 'status_code', 'shop_id', 'product_1_id', 'product_2_id'],
    (
        (1, 201, 1, 1, 2),
        (100, 403, 2, 15, 16),
    )
)
@pytest.mark.django_db
def test_create_delete_order(client, user, contact, products, quantity, status_code, shop_id, product_1_id, product_2_id):
    """
    Проверяет процесс создания нового заказа и его удаление.

    Проверяется, что при успешном создании заказа (HTTP 201):
    - создаётся объект Order с корректным контактом, пользователем и статусом 'new',
    - создаются два связанных OrderItem,
    - при запросе корзины (basket) возвращается корректный список с заказанными товарами.

    Также тестируется удаление элементов заказа и подтверждение заказа через API.
    """

    response = client.post('/api/v1/add_order_items/',
                          data={
                              "contact": contact.id,
                              "order_items": [
                                  {
                                      "product": {"id": product_1_id},
                                      "quantity": quantity,
                                      "shop": shop_id
                                  },
                                  {
                                      "product": {"id": product_2_id},
                                      "quantity": 1,
                                      "shop": shop_id
                                  }
                              ]
                          },
                          headers={
                              'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
                              'Content-Type': 'application/json'
                          })

    response_1 = client.get('/api/v1/basket', headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
        'Content-Type': 'application/json'
    })

    basket = response_1.json()
    order = Order.objects.first()

    assert response.status_code == status_code

    if response.status_code == 201:
        assert order is not None
        assert OrderItem.objects.exists()
        assert order.contact == contact
        assert order.user == user
        assert order.status == 'new'
        assert order.orderitem_set.count() == 2

        assert response_1.status_code == 200
        assert basket[0].get('order') == 1
        assert basket[0].get('product').get('id') == 2
        assert basket[1].get('product').get('id') == 1
        assert basket[0].get('quantity') == 1

        response_to_delete = client.delete('/api/v1/delete_order_item/{100}/', headers={
            'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
            'Content-Type': 'application/json'
        })
        assert response_to_delete.status_code == 404

        response_to_delete = client.delete('/api/v1/delete_order_item/1/', headers={
            'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
            'Content-Type': 'application/json'
        })
        assert response_to_delete.status_code == 204

        response_to_confirm = client.patch('/api/v1/confirm/1/',
                                           data={"status": "confirm"},
                                           headers={
                                               'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
                                               'Content-Type': 'application/json'
                                           })

        order.refresh_from_db()
        assert response_to_confirm.status_code == 200
        assert order.status == 'confirmed'


@pytest.mark.django_db
def test_upload(client, user):
    """
    Проверяет загрузку товаров по ссылке и создание магазина с нужным количеством товаров.
    """
    response = client.post('/api/v1/upload/', data={
        'url': 'https://raw.githubusercontent.com/adlikovskii/diplom/refs/heads/main/shop1.yaml',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
        'Content-Type': 'application/json'
    })

    shop = Shop.objects.get(name='МВидео')
    product_count = Product.objects.count()

    assert response.status_code == 200
    assert shop.name == 'МВидео'
    assert product_count == 14


@pytest.mark.django_db
def test_get_products(client, user, products):
    """
    Проверяет корректность получения списка товаров из API.
    """
    response = client.get('/api/v1/products/', headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:password")}',
        'Content-Type': 'application/json'
    })

    assert response.status_code == 200
    assert products.count() == Product.objects.count()