Моделі бази даних
================

Цей розділ містить документацію для всіх моделей бази даних, які використовуються в Contact Management API.

Огляд моделей
-------------

Система використовує дві основні моделі:

* **User** - для управління користувачами та аутентифікації
* **Contact** - для зберігання інформації про контакти

Обидві моделі використовують SQLAlchemy ORM та підтримують міграції через Alembic.

Модель користувачів
-------------------

.. automodule:: app.models.users
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: app.models.users.User
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __repr__

   .. note::
      Всі паролі зберігаються в хешованому вигляді з використанням bcrypt.
      Токени верифікації та скидання пароля мають обмежений час дії.

   **Приклад використання:**

   .. code-block:: python

      from app.models.users import User, UserRole
      from app.utils.auth import get_password_hash

      # Створення нового користувача
      user = User(
          username='johndoe',
          email='john@example.com',
          hashed_password=get_password_hash('secret123'),
          role=UserRole.USER,
          is_verified=False
      )

      # Перевірка ролі
      if user.is_admin():
          print("Користувач є адміністратором")

.. autoclass:: app.models.users.UserRole
   :members:
   :undoc-members:
   :show-inheritance:

   **Доступні ролі:**

   * ``USER`` - Звичайний користувач з базовими правами
   * ``ADMIN`` - Адміністратор з розширеними правами

Модель контактів
----------------

.. automodule:: app.models.contacts
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: app.models.contacts.Contact
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __repr__

   .. note::
      Email адреса повинна бути унікальною в межах всієї системи.
      Контакти автоматично видаляються при видаленні власника.

   **Приклад використання:**

   .. code-block:: python

      from app.models.contacts import Contact
      from datetime import date

      # Створення нового контакту
      contact = Contact(
          first_name='Іван',
          last_name='Петренко',
          email='ivan@example.com',
          phone_number='+380501234567',
          birth_date=date(1990, 5, 15),
          owner_id=1
      )

      # Використання властивостей
      print(f"Повне ім'я: {contact.full_name}")
      print(f"Вік: {contact.age} років")
      print(f"До дня народження: {contact.days_until_birthday()} днів")

Зв'язки між моделями
-------------------

Моделі User та Contact мають наступні зв'язки:

.. code-block:: python

   # У моделі User
   contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")

   # У моделі Contact  
   owner = relationship("User", back_populates="contacts")

**Каскадне видалення:**

При видаленні користувача автоматично видаляються всі його контакти завдяки налаштуванню ``cascade="all, delete-orphan"``.

**Приклад запиту з join:**

.. code-block:: python

   from sqlalchemy.orm import Session
   from app.models.users import User
   from app.models.contacts import Contact

   # Отримання всіх контактів з інформацією про власника
   contacts_with_owners = session.query(Contact).join(User).all()

   # Отримання користувача з усіма контактами
   user_with_contacts = session.query(User).options(
       joinedload(User.contacts)
   ).filter(User.id == 1).first()

Індекси та оптимізація
---------------------

Моделі мають наступні індекси для оптимізації запитів:

**User модель:**

* ``username`` - унікальний індекс
* ``email`` - унікальний індекс
* ``id`` - первинний ключ (автоматичний індекс)

**Contact модель:**

* ``first_name`` - індекс для пошуку
* ``last_name`` - індекс для пошуку
* ``email`` - унікальний індекс
* ``owner_id`` - зовнішній ключ (автоматичний індекс)
* ``id`` - первинний ключ (автоматичний індекс)

Валідація даних
---------------

Моделі підтримують валідацію на рівні бази даних:

**Обмеження полів:**

* ``User.username`` - до 50 символів, обов'язкове, унікальне
* ``User.email`` - до 100 символів, обов'язкове, унікальне  
* ``Contact.first_name`` - до 50 символів, обов'язкове
* ``Contact.last_name`` - до 50 символів, обов'язкове
* ``Contact.email`` - до 100 символів, обов'язкове, унікальне
* ``Contact.phone_number`` - до 20 символів, обов'язкове

**Nullable поля:**

* ``User.avatar_url`` - може бути NULL
* ``User.verification_token`` - може бути NULL
* ``Contact.additional_data`` - може бути NULL

Міграції
--------

Всі зміни в моделях повинні супроводжуватися міграціями Alembic:

.. code-block:: bash

   # Створення нової міграції
   alembic revision --autogenerate -m "Опис змін"

   # Застосування міграцій
   alembic upgrade head

   # Відкат міграції
   alembic downgrade -1

**Файли міграцій знаходяться в:** ``alembic/versions/``