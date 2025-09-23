Аутентифікація API
==================

Ендпоінти для реєстрації, входу та управління аутентифікацією користувачів.

Реєстрація користувача
----------------------

Реєстрація нового користувача в системі.

.. http:post:: /api/v1/auth/register

   **Приклад запиту:**

   .. code-block:: json

      {
        "username": "johndoe",
        "email": "john@example.com", 
        "password": "SecurePassword123!"
      }

   **Приклад відповіді:**

   .. code-block:: json

      {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "role": "user", 
        "is_verified": false,
        "created_at": "2025-09-23T10:30:00Z"
      }

   :reqjson string username: Ім'я користувача (3-50 символів)
   :reqjson string email: Email адреса
   :reqjson string password: Пароль (мінімум 6 символів)
   :reqjson string role: Роль користувача (опціонально)
   
   :statuscode 201: Користувач успішно створений
   :statuscode 409: Email або username вже зайняті
   :statuscode 422: Некоректні дані

Реєстрація адміністратора
-------------------------

.. http:post:: /api/v1/auth/register-admin

   Спеціальний ендпоінт для створення користувача з роллю admin.

Вхід користувача
----------------

.. http:post:: /api/v1/auth/login

   **Приклад запиту:**

   .. code-block:: json

      {
        "email": "john@example.com",
        "password": "SecurePassword123!"
      }

   **Приклад відповіді:**

   .. code-block:: json

      {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer"
      }

   :reqjson string email: Email адреса
   :reqjson string password: Пароль
   
   :statuscode 200: Успішний вхід
   :statuscode 401: Неправильні credentials

Верифікація Email
-----------------

.. http:get:: /api/v1/auth/verify-email

   Верифікує email адресу користувача за токеном.

   :query token: Токен верифікації з email

Повторна відправка верифікації
------------------------------

.. http:post:: /api/v1/auth/resend-verification

   :query email: Email адреса для повторної відправки

Скидання пароля
---------------

.. http:post:: /api/v1/auth/forgot-password

   Запит на скидання пароля.

.. http:post:: /api/v1/auth/reset-password

   Скидання пароля за токеном.

.. http:get:: /api/v1/auth/verify-reset-token

   Перевірка валідності токена скидання пароля.
