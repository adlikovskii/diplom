from django.contrib import admin
from .models import CustomUser, Contact, ConfirmToken


# Регистрируем модели в админке Django для удобного управления ими
admin.site.register(CustomUser)
admin.site.register(Contact)
admin.site.register(ConfirmToken)