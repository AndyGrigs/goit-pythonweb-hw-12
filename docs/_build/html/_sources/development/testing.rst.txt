Тестування
==========

Інструкції по запуску та підтримці тестів.

Швидкий старт
-------------

.. code-block:: bash

   # Встановити тестові залежності
   make install-test-deps

   # Запустити всі тести
   make test

   # Тільки модульні тести
   make test-unit

   # Тільки інтеграційні тести
   make test-integration

Структура тестів
----------------

.. code-block:: text

   tests/
   ├── conftest.py              # Конфігурація та фікстури
   ├── unit/                    # Модульні тести
   │   ├── test_crud_users.py
   │   ├── test_crud_contacts.py
   │   └── test_utils_auth.py
   └── integration/             # Інтеграційні тести
       ├── test_api_auth.py
       ├── test_api_users.py
       └── test_api_contacts.py

Покриття тестами
----------------

Проект має покриття тестами понад 75%:

.. code-block:: bash

   # Генерація HTML звіту покриття
   make test-html

   # Перегляд звіту
   open htmlcov/index.html

Написання тестів
----------------

Приклад модульного тесту:

.. code-block:: python

   @pytest.mark.unit
   def test_create_user(db_session):
       user_data = UserCreate(
           username="testuser",
           email="test@example.com", 
           password="password123"
       )
       
       user = create_user(db_session, user_data)
       
       assert user.username == "testuser"
       assert user.email == "test@example.com"

Приклад інтеграційного тесту:

.. code-block:: python

   @pytest.mark.integration
   def test_create_contact_api(client, auth_headers):
       contact_data = {
           "first_name": "Іван",
           "last_name": "Петренко",
           "email": "ivan@example.com"
       }
       
       response = client.post(
           "/api/v1/contacts/",
           json=contact_data,
           headers=auth_headers
       )
       
       assert response.status_code == 201
