Налаштування середовища розробки
===================================

Детальна інструкція по налаштуванню проекту для розробки.

Попередні вимоги
----------------

Перед початком роботи переконайтеся, що у вас встановлені:

* Python 3.9 або вище
* Git
* Docker та Docker Compose
* pip та venv

Крок 1: Клонування репозиторію
-------------------------------

.. code-block:: bash

   git clone <your-repo-url>
   cd contact-management-api

Крок 2: Створення віртуального середовища
------------------------------------------

.. code-block:: bash

   # Створення віртуального середовища
   python -m venv venv

   # Активація (Windows)
   venv\Scripts\activate

   # Активація (Linux/Mac)  
   source venv/bin/activate

Крок 3: Встановлення залежностей
---------------------------------

.. code-block:: bash

   # Основні залежності
   pip install -r requirements.txt

   # Залежності для тестування (опціонально)
   pip install -r requirements-test.txt

Крок 4: Налаштування змінних середовища
----------------------------------------

.. code-block:: bash

   # Скопіюйте приклад файлу
   cp .env.example .env

   # Відредагуйте файл .env
   nano .env

Приклад .env файлу:

.. code-block:: text

   # Database
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=contacts_db
   DB_USER=contacts_user
   DB_PASSWORD=contacts_password

   # Security
   SECRET_KEY=your-super-secret-jwt-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Email Configuration
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_FROM=your-email@gmail.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com

   # Cloudinary
   CLOUDINARY_NAME=your-cloudinary-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379

Крок 5: Запуск сервісів
------------------------

.. code-block:: bash

   # Запуск PostgreSQL, Redis та PgAdmin
   docker-compose up -d

   # Перевірка статусу
   docker-compose ps

Крок 6: Виконання міграцій
---------------------------

.. code-block:: bash

   # Застосування міграцій
   alembic upgrade head

   # Створення нової міграції (за потреби)
   alembic revision --autogenerate -m "Опис змін"

Крок 7: Запуск сервера розробки
--------------------------------

.. code-block:: bash

   # Запуск з auto-reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Корисні команди
---------------

.. code-block:: bash

   # Перевірка здоров'я API
   curl http://localhost:8000/health

   # Доступ до API документації
   open http://localhost:8000/docs

   # Доступ до PgAdmin
   open http://localhost:8080

   # Перегляд логів Docker
   docker-compose logs -f

Налаштування IDE
----------------

VS Code
~~~~~~~

Рекомендовані розширення:

* Python
* Pylance  
* Python Docstring Generator
* REST Client
* Docker

Налаштування .vscode/settings.json:

.. code-block:: json

   {
       "python.defaultInterpreterPath": "./venv/bin/python",
       "python.linting.enabled": true,
       "python.linting.pylintEnabled": true,
       "python.formatting.provider": "black",
       "python.testing.pytestEnabled": true,
       "python.testing.pytestArgs": ["tests/"]
   }

PyCharm
~~~~~~~

1. Налаштуйте Python інтерпретатор на віртуальне середовище
2. Встановіть pytest як test runner
3. Налаштуйте автоматичне форматування з black
