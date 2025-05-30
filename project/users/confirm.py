from django.conf import settings
from django.core.mail import EmailMessage


def send_email(email, token, recipient):
    """
    Отправляет письмо с ссылкой для подтверждения email.

    Аргументы:
        email (str): Email для подтверждения.
        token (str): Токен подтверждения.
        recipient (list): Список получателей письма.
    """
    confirmation_url = (
        f"http://127.0.0.1:8000/api/v1/confirm_email/{token}/{email}"
    )
    message_body = f"""
        Для завершения регистрации, пожалуйста, перейдите по ссылке:
        <a href="{confirmation_url}">Подтвердить email</a>
    """
    email_message = EmailMessage(
        "Регистрация на retail-сайте",
        message_body,
        settings.EMAIL_HOST_USER,
        recipient,
    )
    email_message.content_subtype = "html"
    email_message.send()


def send_confirmed_order(order_info, recipient):
    """
    Отправляет подтверждение заказа клиенту и администратору.

    Аргументы:
        order_info (dict): Данные по заказу, включая товары и итоговую сумму.
        recipient (list): Список email-адресов клиента.
    """
    products_description = ""
    for product_name, details in order_info["products"].items():
        products_description += (
            f"{product_name} x {details['quantity']}, "
            f"итоговая стоимость: {details['total price']}, "
            f"идентификатор товара: {details['id']}\n"
        )

    user_message = f"""
    <pre>
    Ваш заказ #{order_info['order_id']} подтверждён.
    В заказе:
{products_description}
    Общая сумма: {order_info['price_order']}
    Благодарим за покупку!
    </pre>
    """

    admin_message = f"""
    <pre>
    Пользователь {order_info['user']} подтвердил заказ №{order_info['order_id']}.
    Состав заказа:
{products_description}
    Итоговая стоимость: {order_info['price_order']}
    </pre>
    """

    # Письмо клиенту
    user_email = EmailMessage(
        "Подтверждение заказа на retail-сайте",
        user_message,
        settings.EMAIL_HOST_USER,
        recipient,
    )
    user_email.content_subtype = "html"
    user_email.send()

    # Письмо администратору
    admin_email = EmailMessage(
        "Подтверждён заказ на retail-сайте",
        admin_message,
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
    )
    admin_email.content_subtype = "html"
    admin_email.send()
