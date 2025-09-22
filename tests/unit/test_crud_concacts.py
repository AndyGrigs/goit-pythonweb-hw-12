import pytest
from datetime import date, timedelta
from app.crud.contacts import (
    get_contact,
    get_contacts,
    create_contact,
    update_contact,
    delete_contact,
    get_contacts_with_upcoming_birthdays
)
from app.schemas.contacts import ContactCreate, ContactUpdate
from app.models.contacts import Contact


@pytest.mark.unit
@pytest.mark.crud
class TestContactCRUD:
    """Тести для CRUD операцій контактів"""
    
    def test_get_contact_existing_owner(self, db_session, create_test_contact, create_test_user):
        """Тест отримання контакту власником"""
        contact = get_contact(db_session, create_test_contact.id, create_test_user.id)
        
        assert contact is not None
        assert contact.id == create_test_contact.id
        assert contact.owner_id == create_test_user.id
    
    def test_get_contact_not_owner(self, db_session, create_test_contact):
        """Тест отримання контакту не власником"""
        other_user_id = 999
        contact = get_contact(db_session, create_test_contact.id, other_user_id)
        assert contact is None
    
    def test_get_contact_not_existing(self, db_session, create_test_user):
        """Тест отримання неіснуючого контакту"""
        contact = get_contact(db_session, 99999, create_test_user.id)
        assert contact is None
    
    def test_get_contacts_by_owner(self, db_session, create_test_user):
        """Тест отримання контактів власника"""
        # Створюємо кілька контактів для користувача
        contact1 = Contact(
            first_name="Іван",
            last_name="Петренко",
            email="ivan@example.com",
            phone_number="+380501234567",
            birth_date=date(1990, 5, 15),
            owner_id=create_test_user.id
        )
        contact2 = Contact(
            first_name="Марія",
            last_name="Коваленко",
            email="maria@example.com",
            phone_number="+380671234567",
            birth_date=date(1985, 12, 25),
            owner_id=create_test_user.id
        )
        
        db_session.add_all([contact1, contact2])
        db_session.commit()
        
        contacts = get_contacts(db_session, create_test_user.id)
        
        assert len(contacts) == 2
        assert all(contact.owner_id == create_test_user.id for contact in contacts)
    
    def test_get_contacts_with_search(self, db_session, create_test_user):
        """Тест отримання контактів з пошуком"""
        # Створюємо контакти
        contact1 = Contact(
            first_name="Іван",
            last_name="Петренко",
            email="ivan@example.com",
            phone_number="+380501234567",
            birth_date=date(1990, 5, 15),
            owner_id=create_test_user.id
        )
        contact2 = Contact(
            first_name="Марія",
            last_name="Коваленко",
            email="maria@example.com",
            phone_number="+380671234567",
            birth_date=date(1985, 12, 25),
            owner_id=create_test_user.id
        )
        
        db_session.add_all([contact1, contact2])
        db_session.commit()
        
        # Пошук за іменем
        contacts = get_contacts(db_session, create_test_user.id, search="Іван")
        assert len(contacts) == 1
        assert contacts[0].first_name == "Іван"
        
        # Пошук за прізвищем
        contacts = get_contacts(db_session, create_test_user.id, search="Коваленко")
        assert len(contacts) == 1
        assert contacts[0].last_name == "Коваленко"
        
        # Пошук за email
        contacts = get_contacts(db_session, create_test_user.id, search="maria@")
        assert len(contacts) == 1
        assert "maria@" in contacts[0].email
    
    def test_get_contacts_with_pagination(self, db_session, create_test_user):
        """Тест отримання контактів з пагінацією"""
        # Створюємо 5 контактів
        contacts = []
        for i in range(5):
            contact = Contact(
                first_name=f"User{i}",
                last_name=f"Lastname{i}",
                email=f"user{i}@example.com",
                phone_number=f"+38050123456{i}",
                birth_date=date(1990, 1, 1),
                owner_id=create_test_user.id
            )
            contacts.append(contact)
        
        db_session.add_all(contacts)
        db_session.commit()
        
        # Тест skip=0, limit=3
        result = get_contacts(db_session, create_test_user.id, skip=0, limit=3)
        assert len(result) == 3
        
        # Тест skip=2, limit=3
        result = get_contacts(db_session, create_test_user.id, skip=2, limit=3)
        assert len(result) == 3
    
    def test_create_contact_success(self, db_session, create_test_user):
        """Тест успішного створення контакту"""
        contact_data = ContactCreate(
            first_name="Новий",
            last_name="Контакт",
            email="new@example.com",
            phone_number="+380991234567",
            birth_date=date(1992, 8, 22),
            additional_data="Новий тестовий контакт"
        )
        
        created_contact = create_contact(db_session, contact_data, create_test_user.id)
        
        assert created_contact.first_name == contact_data.first_name
        assert created_contact.last_name == contact_data.last_name
        assert created_contact.email == contact_data.email
        assert created_contact.phone_number == contact_data.phone_number
        assert created_contact.birth_date == contact_data.birth_date
        assert created_contact.additional_data == contact_data.additional_data
        assert created_contact.owner_id == create_test_user.id
        assert created_contact.id is not None
    
    def test_update_contact_success(self, db_session, create_test_contact, create_test_user):
        """Тест успішного оновлення контакту"""
        update_data = ContactUpdate(
            first_name="Оновлений",
            last_name="Контакт",
            additional_data="Оновлені дані"
        )
        
        updated_contact = update_contact(
            db_session, 
            create_test_contact.id, 
            update_data, 
            create_test_user.id
        )
        
        assert updated_contact is not None
        assert updated_contact.first_name == "Оновлений"
        assert updated_contact.last_name == "Контакт"
        assert updated_contact.additional_data == "Оновлені дані"
        # Email не змінився
        assert updated_contact.email == create_test_contact.email
    
    def test_update_contact_not_owner(self, db_session, create_test_contact):
        """Тест оновлення контакту не власником"""
        update_data = ContactUpdate(first_name="Хакер")
        other_user_id = 999
        
        updated_contact = update_contact(
            db_session, 
            create_test_contact.id, 
            update_data, 
            other_user_id
        )
        
        assert updated_contact is None
    
    def test_update_contact_not_existing(self, db_session, create_test_user):
        """Тест оновлення неіснуючого контакту"""
        update_data = ContactUpdate(first_name="Оновлений")
        
        updated_contact = update_contact(
            db_session, 
            99999, 
            update_data, 
            create_test_user.id
        )
        
        assert updated_contact is None
    
    def test_delete_contact_success(self, db_session, create_test_contact, create_test_user):
        """Тест успішного видалення контакту"""
        contact_id = create_test_contact.id
        
        result = delete_contact(db_session, contact_id, create_test_user.id)
        
        assert result is True
        
        # Перевіряємо, що контакт дійсно видалений
        deleted_contact = get_contact(db_session, contact_id, create_test_user.id)
        assert deleted_contact is None
    
    def test_delete_contact_not_owner(self, db_session, create_test_contact):
        """Тест видалення контакту не власником"""
        other_user_id = 999
        
        result = delete_contact(db_session, create_test_contact.id, other_user_id)
        
        assert result is False
        
        # Перевіряємо, що контакт не видалений
        contact = db_session.query(Contact).filter(Contact.id == create_test_contact.id).first()
        assert contact is not None
    
    def test_delete_contact_not_existing(self, db_session, create_test_user):
        """Тест видалення неіснуючого контакту"""
        result = delete_contact(db_session, 99999, create_test_user.id)
        assert result is False
    
    def test_get_contacts_with_upcoming_birthdays(self, db_session, create_test_user):
        """Тест отримання контактів з днями народження на найближчі 7 днів"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=6)
        far_future = today + timedelta(days=30)
        past_date = today - timedelta(days=30)
        
        # Створюємо контакти з різними днями народження
        contact_tomorrow = Contact(
            first_name="Завтра",
            last_name="Народження",
            email="tomorrow@example.com",
            phone_number="+380501234567",
            birth_date=date(1990, tomorrow.month, tomorrow.day),
            owner_id=create_test_user.id
        )
        
        contact_next_week = Contact(
            first_name="Наступний",
            last_name="Тиждень",
            email="nextweek@example.com",
            phone_number="+380671234567",
            birth_date=date(1985, next_week.month, next_week.day),
            owner_id=create_test_user.id
        )
        
        contact_far_future = Contact(
            first_name="Далеко",
            last_name="Майбутнє",
            email="future@example.com",
            phone_number="+380991234567",
            birth_date=date(1992, far_future.month, far_future.day),
            owner_id=create_test_user.id
        )
        
        contact_past = Contact(
            first_name="Минуле",
            last_name="Народження",
            email="past@example.com",
            phone_number="+380631234567",
            birth_date=date(1988, past_date.month, past_date.day),
            owner_id=create_test_user.id
        )
        
        db_session.add_all([contact_tomorrow, contact_next_week, contact_far_future, contact_past])
        db_session.commit()
        
        # Отримуємо контакти з днями народження на найближчі 7 днів
        upcoming_birthdays = get_contacts_with_upcoming_birthdays(db_session, create_test_user.id)
        
        # Мають бути тільки контакти з днями народження завтра та наступного тижня
        expected_emails = {"tomorrow@example.com", "nextweek@example.com"}
        actual_emails = {contact.email for contact in upcoming_birthdays}
        
        assert actual_emails == expected_emails
        assert len(upcoming_birthdays) == 2
    
    def test_get_contacts_with_upcoming_birthdays_empty(self, db_session, create_test_user):
        """Тест отримання контактів з днями народження (порожній результат)"""
        far_future = date.today() + timedelta(days=30)
        
        # Створюємо контакт з днем народження далеко в майбутньому
        contact = Contact(
            first_name="Далеко",
            last_name="Майбутнє",
            email="future@example.com",
            phone_number="+380991234567",
            birth_date=date(1992, far_future.month, far_future.day),
            owner_id=create_test_user.id
        )
        
        db_session.add(contact)
        db_session.commit()
        
        upcoming_birthdays = get_contacts_with_upcoming_birthdays(db_session, create_test_user.id)
        assert len(upcoming_birthdays) == 0
    
    def test_get_contacts_different_owners(self, db_session, create_test_user, db_session_factory=None):
        """Тест що користувачі бачать тільки свої контакти"""
        # Створюємо другого користувача
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=True
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)
        
        # Створюємо контакти для обох користувачів
        contact1 = Contact(
            first_name="Контакт",
            last_name="Першого",
            email="contact1@example.com",
            phone_number="+380501234567",
            birth_date=date(1990, 5, 15),
            owner_id=create_test_user.id
        )
        
        contact2 = Contact(
            first_name="Контакт",
            last_name="Другого",
            email="contact2@example.com",
            phone_number="+380671234567",
            birth_date=date(1985, 12, 25),
            owner_id=user2.id
        )
        
        db_session.add_all([contact1, contact2])
        db_session.commit()
        
        # Перевіряємо, що кожен користувач бачить тільки свої контакти
        user1_contacts = get_contacts(db_session, create_test_user.id)
        user2_contacts = get_contacts(db_session, user2.id)
        
        assert len(user1_contacts) == 1
        assert len(user2_contacts) == 1
        assert user1_contacts[0].owner_id == create_test_user.id
        assert user2_contacts[0].owner_id == user2.id
        assert user1_contacts[0].email == "contact1@example.com"
        assert user2_contacts[0].email == "contact2@example.com"