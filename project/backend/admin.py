from django.contrib import admin
from .models import (
    Shop,
    Order,
    OrderItem,
    Product,
    ProductInfo,
    ProductParameter,
    Parameter,
    Category
)

# Регистрируем модели для отображения в админке
models_to_register = [
    Shop,
    Order,
    OrderItem,
    Product,
    ProductInfo,
    ProductParameter,
    Parameter,
    Category
]

for model in models_to_register:
    admin.site.register(model)