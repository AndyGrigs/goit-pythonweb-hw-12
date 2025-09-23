Контакти API
============

Ендпоінти для управління контактами користувачів.

Створення контакту
------------------

.. http:post:: /api/v1/contacts/

   **Приклад запиту:**

   .. code-block:: json

      {
        "first_name": "Іван",
        "last_name": "Петренко",
        "email": "ivan@example.com", 
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Друг з університету"
      }

   **Приклад відповіді:**

   .. code-block:: json

      {
        "id": 1,
        "first_name": "Іван",
        "last_name": "Петренко", 
        "email": "ivan@example.com",
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Друг з університету",
        "owner_id": 1
      }

   :reqjson string first_name: Ім'я (обов'язкове)
   :reqjson string last_name: Прізвище (обов'язкове)
   :reqjson string email: Email адреса (унікальна)
   :reqjson string phone_number: Номер телефону
   :reqjson string birth_date: Дата народження (YYYY-MM-DD)
   :reqjson string additional_data: Додаткові дані (опціонально)

   :statuscode 201: Контакт створено
   :statuscode 400: Email вже існує або некоректні дані
   :statuscode 401: Не авторизований

Отримання списку контактів
--------------------------

.. http:get:: /api/v1/contacts/

   :query skip: Кількість записів для пропуску (за замовчуванням 0)
   :query limit: Максимальна кількість записів (за замовчуванням 100)
   :query search: Пошук за іменем, прізвищем або email

   **Приклад з пошуком:**

   .. code-block:: text

      GET /api/v1/contacts/?search=Іван&skip=0&limit=10

Отримання контакту за ID
------------------------

.. http:get:: /api/v1/contacts/{contact_id}

   :param contact_id: ID контакту

   :statuscode 200: Контакт знайдено
   :statuscode 404: Контакт не знайдено

Оновлення контакту
------------------

.. http:put:: /api/v1/contacts/{contact_id}

   **Приклад запиту:**

   .. code-block:: json

      {
        "first_name": "Іван",
        "additional_data": "Оновлені дані"
      }

   :param contact_id: ID контакту

Видалення контакту
------------------

.. http:delete:: /api/v1/contacts/{contact_id}

   :param contact_id: ID контакту

   **Приклад відповіді:**

   .. code-block:: json

      {
        "message": "Contact deleted successfully!"
      }

Дні народження
--------------

.. http:get:: /api/v1/contacts/birthdays/

   Повертає контакти з днями народження на найближчі 7 днів.

   **Приклад відповіді:**

   .. code-block:: json

      [
        {
          "id": 1,
          "first_name": "Марія",
          "last_name": "Коваленко",
          "birth_date": "1985-12-25",
          "email": "maria@example.com"
        }
      ]
