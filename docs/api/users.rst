Користувачі API
===============

Ендпоінти для управління профілями користувачів.

Отримання поточного користувача
-------------------------------

.. http:get:: /api/v1/users/me

   **Заголовки:**

   .. code-block:: text

      Authorization: Bearer YOUR_JWT_TOKEN

   **Приклад відповіді:**

   .. code-block:: json

      {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "avatar_url": "https://cloudinary.com/avatar.jpg",
        "role": "user",
        "is_verified": true,
        "created_at": "2025-09-23T10:30:00Z"
      }

   :statuscode 200: Успішно
   :statuscode 401: Не авторизований
   :statuscode 400: Email не верифікований

   .. note::
      Цей ендпоінт має rate limiting: максимум 10 запитів на хвилину.

Завантаження аватара
--------------------

.. http:post:: /api/v1/users/me/avatar

   **Тільки для адміністраторів**

   Завантажує аватар користувача в Cloudinary.

   :form file: Файл зображення (максимум 5MB)

   :statuscode 200: Аватар завантажено
   :statuscode 400: Некоректний файл або занадто великий
   :statuscode 403: Потрібні права адміністратора

Зміна ролі користувача
----------------------

.. http:patch:: /api/v1/users/{user_id}/role

   **Тільки для адміністраторів**

   **Приклад запиту:**

   .. code-block:: json

      {
        "role": "admin"
      }

   :param user_id: ID користувача
   :reqjson string role: Нова роль (user/admin)

   :statuscode 200: Роль змінена
   :statuscode 400: Адмін не може понизити себе
   :statuscode 403: Потрібні права адміністратора
   :statuscode 404: Користувач не знайдений
