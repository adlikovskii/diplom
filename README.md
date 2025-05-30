
# 🛒 Retail API — дипломный проект на Django REST Framework

## О проекте
**Retail API** — backend-приложение, созданное с использованием Django REST Framework, предназначенное для автоматизации процесса оформления заказов в розничной торговле. Проект реализует RESTful API для работы с товарами, заказами и пользователями.

---

## Функциональность
- Аутентификация и регистрация пользователей через email
- Импорт товаров из YAML-файлов по URL
- Создание и редактирование заказов с добавлением/удалением товаров
- Обновление профиля и контактной информации пользователя
- Просмотр списка товаров, заказов и контактов
- Подтверждение оформления заказа

---

## Технологии
- Python 3.x  
- Django 4.x + Django REST Framework  
- PostgreSQL 15  
- Docker и Docker Compose  

---

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/adlikovskii/diplom.git
   cd project
   ```

2. Соберите Docker-образы:
   ```bash
   docker-compose build
   ```

3. Запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

4. Создайте суперпользователя:
   ```bash
   docker exec -it <название-контейнера-с-джанго> python manage.py createsuperuser
   ```
   *Пример: `docker exec -it diplom-web-1 python manage.py createsuperuser`*

---

## Использование API

Откройте в браузере:  
[http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

Или используйте Postman / curl для отправки запросов.

---

## Примеры запросов

### Загрузка товаров из файла

**POST** `/api/v1/upload/`

Тело запроса:
```json
{
  "url": "https://raw.githubusercontent.com/adlikovskii/diplom/refs/heads/main/shop1.yaml"
}
```

---

### Добавление контактной информации

**POST** `/api/v1/add_contact/`

Тело запроса:
```json
{
  "city": "Москва",
  "street": "Ленина",
  "house": "10",
  "apartment": "4",
  "user": 1,
  "phone": "89008007766"
}
```

---

### Получение списка товаров

**GET** `/api/v1/products/`

---

### Добавление товаров в заказ

**POST** `/api/v1/add_order_items/`

Тело запроса:
```json
{
  "contact": 1,
  "order_items": [
    {
      "product": { "id": 1 },
      "quantity": 1,
      "shop": 2
    },
    {
      "product": { "id": 3 },
      "quantity": 1,
      "shop": 2
    }
  ]
}
```

