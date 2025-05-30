from django.db import models
from django.conf import settings

from users.models import Contact


ORDER_STATUS = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Shop(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        blank=True,
        null=True
    )
    url = models.URLField(max_length=255, verbose_name='Ссылка', blank=True, null=True)

    class Meta:
        ordering = ['-name']
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазины', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID')
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        ordering = ['-name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=80, verbose_name='Название')

    class Meta:
        ordering = ['-name']
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_info', verbose_name='Продукт', blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_info', verbose_name='Магазин', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID')
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Розничная цена')

    class Meta:
        ordering = ['-model']
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['external_id', 'shop'], name='unique_product_info')
        ]

    def __str__(self):
        return f'{self.product} : {self.quantity} pcs'


class Parameter(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')

    class Meta:
        ordering = ['-name']
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имён параметров'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='product_parameters', verbose_name='Информация о продукте', blank=True)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters', verbose_name='Параметр', blank=True)
    value = models.CharField(max_length=150, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')
        ]

    def __str__(self):
        return f'{self.product_info.model} - {self.parameter.name}: {self.value}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(max_length=12, choices=ORDER_STATUS, default='new', verbose_name='Статус')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, verbose_name='Контактная информация', blank=True)

    class Meta:
        ordering = ['-dt']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'

    def __str__(self):
        return f'Статус: {self.status} / Пользователь: {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Список заказанных позиций'

    def __str__(self):
        return f'{self.order} | {self.product} × {self.quantity} шт.'

    def save(self, *args, **kwargs):
        # Расчет общей стоимости с учетом рекомендованной розничной цены
        self.total_price = self.quantity * self.product.product_info.first().price_rrc
        super().save(*args, **kwargs)