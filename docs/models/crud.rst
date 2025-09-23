CRUD операції
=============

Цей розділ описує всі CRUD (Create, Read, Update, Delete) операції для роботи з користувачами та контактами в системі.

Огляд CRUD модулів
------------------

CRUD операції організовані в два основні модулі:

* **users.py** - операції з користувачами, аутентифікація, управління ролями
* **contacts.py** - операції з контактами, пошук, фільтрація

CRUD користувачів
-----------------

.. automodule:: app.crud.users
   :members:
   :undoc-members:
   :show-inheritance:

Функції аутентифікації
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.users.get_current_user

.. autofunction:: app.crud.users.get_current_verified_user

.. autofunction:: app.crud.users.get_current_admin_user

.. autofunction:: app.crud.users.authenticate_user

Основні CRUD операції
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.users.get_user_by_email

.. autofunction:: app.crud.users.get_user_by_username

.. autofunction:: app.crud.users.get_user_by_id

.. autofunction:: app.crud.users.get_all_users

.. autofunction:: app.crud.users.create_user

.. autofunction:: app.crud.users.update_user

.. autofunction:: app.crud.users.update_user_role

.. autofunction:: app.crud.users.update_user_avatar

Управління паролями
~~~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.users.create_password_reset_token

.. autofunction:: app.crud.users.reset_user_password

.. autofunction:: app.crud.users.verify_reset_token

Верифікація email
~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.users.verify_user_email

Утиліти кешування
~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.users.user_dict_to_model

.. autofunction:: app.crud.users.user_model_to_dict

.. autofunction:: app.crud.users.invalidate_user_cache

.. autofunction:: app.crud.users.require_role

**Приклади використання CRUD користувачів:**

.. code-block:: python

   from app.crud.users import (
       create_user, authenticate_user, get_user_by_email
   )
   from app.schemas.users import UserCreate
   from app.models.users import UserRole

   # Створення користувача
   user_data = UserCreate(
       username="newuser",
       email="user@example.com", 
       password="securepassword123",
       role=UserRole.USER
   )
   new_user = create_user(db, user_data)

   # Аутентифікація
   user = authenticate_user(db, "user@example.com", "securepassword123")
   if user:
       print(f"Аутентифікація успішна: {user.username}")

   # Пошук користувача
   found_user = get_user_by_email(db, "user@example.com")

CRUD контактів
--------------

.. automodule:: app.crud.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Основні операції
~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.contacts.get_contact

.. autofunction:: app.crud.contacts.get_contacts

.. autofunction:: app.crud.contacts.create_contact

.. autofunction:: app.crud.contacts.update_contact

.. autofunction:: app.crud.contacts.delete_contact

Спеціальні функції
~~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.contacts.get_contacts_with_upcoming_birthdays

**Приклади використання CRUD контактів:**

.. code-block:: python

   from app.crud.contacts import (
       create_contact, get_contacts, get_contacts_with_upcoming_birthdays
   )
   from app.schemas.contacts import ContactCreate
   from datetime import date

   # Створення контакту
   contact_data = ContactCreate(
       first_name="Іван",
       last_name="Петренко",
       email="ivan@example.com",
       phone_number="+380501234567",
       birth_date=date(1990, 5, 15),
       additional_data="Друг з університету"
   )
   new_contact = create_contact(db, contact_data, owner_id=1)

   # Отримання контактів з пошуком
   contacts = get_contacts(
       db, 
       owner_id=1, 
       skip=0, 
       limit=10, 
       search="Іван"
   )

   # Дні народження на наступні 7 днів
   upcoming_birthdays = get_contacts_with_upcoming_birthdays(db, owner_id=1)

Безпека та авторизація
----------------------

Всі CRUD операції з контактами перевіряють права власності:

.. code-block:: python

   # Правильно - користувач може отримати тільки свої контакти
   user_contacts = get_contacts(db, owner_id=current_user.id)

   # Правильно - користувач може оновити тільки свій контакт
   updated_contact = update_contact(
       db, 
       contact_id=123, 
       contact_update=update_data,
       owner_id=current_user.id  # Обов'язкова перевірка власності
   )

**Middleware авторизації:**

Система використовує middleware для автоматичної перевірки JWT токенів:

.. code-block:: python

   # У API ендпоінтах
   @router.get("/contacts/")
   def get_user_contacts(
       current_user: User = Depends(get_current_verified_user),
       db: Session = Depends(get_db)
   ):
       return get_contacts(db, owner_id=current_user.id)

Кешування користувачів
-----------------------

Система використовує Redis для кешування даних користувачів:

**Процес кешування:**

1. Перевірка кешу при аутентифікації
2. Завантаження з БД якщо немає в кеші  
3. Збереження в кеш після завантаження
4. Інвалідація кешу при оновленнях

.. code-block:: python

   # Автоматичне кешування в get_current_user
   cached_user_data = redis_service.get_user_cache(email)
   if cached_user_data:
       return user_dict_to_model(cached_user_data)
   
   # Завантаження з БД та кешування
   user = get_user_by_email(db, email)
   redis_service.set_user_cache(email, user_model_to_dict(user))

Обробка помилок
---------------

CRUD функції повертають ``None`` або ``False`` замість викидання винятків:

.. code-block:: python

   # Перевірка результатів
   user = get_user_by_id(db, user_id)
   if not user:
       raise HTTPException(status_code=404, detail="User not found")

   # Безпечне видалення
   success = delete_contact(db, contact_id, owner_id)
   if not success:
       raise HTTPException(status_code=404, detail="Contact not found")

Оптимізація запитів
-------------------

**Індексація:**

* Всі поля пошуку мають індекси
* Foreign keys автоматично індексуються
* Composite індекси для частих запитів

**Пагінація:**

.. code-block:: python

   # Ефективна пагінація з OFFSET/LIMIT
   contacts = get_contacts(
       db, 
       owner_id=user_id,
       skip=page * per_page,    # OFFSET
       limit=per_page           # LIMIT
   )

**Пошук:**

.. code-block:: python

   # Ефективний пошук з ILIKE та індексами
   search_filter = or_(
       Contact.first_name.ilike(f"%{search}%"),
       Contact.last_name.ilike(f"%{search}%"), 
       Contact.email.ilike(f"%{search}%")
   )

Транзакції
----------

CRUD операції використовують транзакції SQLAlchemy:

.. code-block:: python

   def create_contact(db: Session, contact: ContactCreate, owner_id: int):
       db_contact = Contact(**contact.model_dump(), owner_id=owner_id)
       db.add(db_contact)
       db.commit()           # Автоматичний rollback при помилці
       db.refresh(db_contact)
       return db_contact

**Для складних операцій:**

.. code-block:: python

   try:
       # Множинні операції в одній транзакції
       db.add(user)
       db.add(contact)
       db.commit()
   except IntegrityError:
       db.rollback()
       raise HTTPException(status_code=400, detail="Data conflict")

Валідація даних
---------------

CRUD функції працюють з Pydantic схемами для валідації:

.. code-block:: python

   from app.schemas.users import UserCreate, UserUpdate
   from app.schemas.contacts import ContactCreate, ContactUpdate

   # Автоматична валідація через Pydantic
   def create_user(db: Session, user: UserCreate) -> User:
       # user вже провалідований Pydantic
       hashed_password = get_password_hash(user.password)
       # ...

   # Часткове оновлення з exclude_unset
   def update_contact(db: Session, contact_id: int, contact_update: ContactUpdate):
       update_data = contact_update.model_dump(exclude_unset=True)
       # Оновлюємо тільки надані поля