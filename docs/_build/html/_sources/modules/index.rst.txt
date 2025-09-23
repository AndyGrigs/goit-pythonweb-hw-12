Документація модулів
====================

Цей розділ містить автоматично згенеровану документацію всіх модулів проекту.

.. toctree::
   :maxdepth: 2
   
   models
   crud
   services
   utils

Структура проекту
-----------------

.. code-block:: text

   app/
   ├── main.py                 # Головний файл додатку
   ├── config.py              # Налаштування
   ├── api/                    # API роутери
   │   ├── deps.py            # Залежності
   │   └── v1/                # API версії 1
   │       ├── api.py         # Головний роутер
   │       └── endpoints/     # Ендпоінти
   ├── models/                # SQLAlchemy моделі
   │   ├── users.py           # Модель користувачів
   │   └── contacts.py        # Модель контактів
   ├── schemas/               # Pydantic схеми
   │   ├── users.py           # Схеми користувачів
   │   └── contacts.py        # Схеми контактів
   ├── crud/                  # CRUD операції
   │   ├── users.py           # CRUD користувачів
   │   └── contacts.py        # CRUD контактів
   ├── services/              # Бізнес логіка
   │   ├── email.py           # Email сервіс
   │   ├── redis.py           # Redis кешування
   │   └── cloudinary.py      # Завантаження файлів
   ├── middleware/            # Middleware
   │   ├── auth.py            # Аутентифікація
   │   └── rate_limiter.py    # Rate limiting
   ├── utils/                 # Утиліти
   │   └── auth.py            # JWT утиліти
   └── database/              # База даних
       ├── base.py            # Базовий клас
       └── connection.py      # З'єднання
