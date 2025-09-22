import pytest
from fastapi import status
from datetime import date, timedelta


@pytest.mark.integration
@pytest.mark.api
class TestContactsAPI:
    """Інтеграційні тести для API контактів"""
    
    def test_create_contact_success(self, client, auth_headers, test_contact_data, mock_all_external_services):
        """Тест успішного створення контакту"""
        response = client.post("/api/v1/contacts/", json=test_contact_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["first_name"] == test_contact_data["first_name"]
        assert data["last_name"] == test_contact_data["last_name"]
        assert data["email"] == test_contact_data["email"]
        assert data["phone_number"] == test_contact_data["phone_number"]
        assert data["birth_date"] == test_contact_data["birth_date"]
        assert data["additional_data"] == test_contact_data["additional_data"]
        assert "id" in data
        assert "owner_id" in data
    
    def test_create_contact_unauthorized(self, client, test_contact_data, mock_all_external_services):
        """Тест створення контакту без авторизації"""
        response = client.post("/api/v1/contacts/", json=test_contact_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_contact_unverified_user(self, client, db_session, test_contact_data, mock_all_external_services):
        """Тест створення контакту неверифікованим користувачем"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash, create_access_token
        from datetime import timedelta
        
        # Створюємо неверифікованого користувача
        unverified_user = User(
            username="unverified",
            email="unverified@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=False
        )
        db_session.add(unverified_user)
        db_session.commit()
        
        # Створюємо токен
        token = create_access_token(
            data={"sub": unverified_user.email, "role": unverified_user.role.value},
            expires_delta=timedelta(minutes=30)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/contacts/", json=test_contact_data, headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not verified" in response.json()["detail"]
    
    def test_create_contact_duplicate_email(self, client, auth_headers, create_test_contact, mock_all_external_services):
        """Тест створення контакту з існуючим email"""
        duplicate_data = {
            "first_name": "Новий",
            "last_name": "Контакт",
            "email": create_test_contact.email,  # Дублікат email
            "phone_number": "+380991234567",
            "birth_date": "1992-08-22",
            "additional_data": "Дублікат"
        }
        
        response = client.post("/api/v1/contacts/", json=duplicate_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already in the system" in response.json()["detail"]
    
    def test_create_contact_invalid_data(self, client, auth_headers, mock_all_external_services):
        """Тест створення контакту з невалідними даними"""
        invalid_data = {
            "first_name": "",  # Порожнє ім'я
            "last_name": "Тест",
            "email": "invalid-email",  # Невалідний email
            "phone_number": "123",  # Невалідний телефон
            "birth_date": "invalid-date"  # Невалідна дата
        }
        
        response = client.post("/api/v1/contacts/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_contacts_empty_list(self, client, auth_headers, mock_all_external_services):
        """Тест отримання порожнього списку контактів"""
        response = client.get("/api/v1/contacts/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_contacts_with_data(self, client, auth_headers, create_test_contact, mock_all_external_services):
        """Тест отримання списку контактів з даними"""
        response = client.get("/api/v1/contacts/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == create_test_contact.id
        assert data[0]["email"] == create_test_contact.email
    
    def test_get_contacts_with_search(self, client, auth_headers, create_test_user, db_session, mock_all_external_services):
        """Тест отримання контактів з пошуком"""
        from app.models.contacts import Contact
        
        # Створюємо кілька контактів
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
        response = client.get("/api/v1/contacts/?search=Іван", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Іван"
        
        # Пошук за email
        response = client.get("/api/v1/contacts/?search=maria", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert "maria" in data[0]["email"]
    
    def test_get_contacts_with_pagination(self, client, auth_headers, create_test_user, db_session, mock_all_external_services):
        """Тест отримання контактів з пагінацією"""
        from app.models.contacts import Contact
        
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
        response = client.get("/api/v1/contacts/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        
        # Тест skip=2, limit=3
        response = client.get("/api/v1/contacts/?skip=2&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
    
    def test_get_contact_by_id_success(self, client, auth_headers, create_test_contact, mock_all_external_services):
        """Тест отримання контакту за ID"""
        response = client.get(f"/api/v1/contacts/{create_test_contact.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == create_test_contact.id
        assert data["email"] == create_test_contact.email
    
    def test_get_contact_by_id_not_found(self, client, auth_headers, mock_all_external_services):
        """Тест отримання неіснуючого контакту"""
        response = client.get("/api/v1/contacts/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_get_contact_by_id_not_owner(self, client, create_test_contact, db_session, mock_all_external_services):
        """Тест отримання чужого контакту"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash, create_access_token
        from datetime import timedelta
        
        # Створюємо другого користувача
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Створюємо токен для другого користувача
        token = create_access_token(
            data={"sub": other_user.email, "role": other_user.role.value},
            expires_delta=timedelta(minutes=30)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/v1/contacts/{create_test_contact.id}", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_contact_success(self, client, auth_headers, create_test_contact, mock_all_external_services):
        """Тест успішного оновлення контакту"""
        update_data = {
            "first_name": "Оновлене",
            "last_name": "Ім'я",
            "additional_data": "Оновлені дані"
        }
        
        response = client.put(f"/api/v1/contacts/{create_test_contact.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Оновлене"
        assert data["last_name"] == "Ім'я"
        assert data["additional_data"] == "Оновлені дані"
        # Email залишається той самий
        assert data["email"] == create_test_contact.email
    
    def test_update_contact_not_found(self, client, auth_headers, mock_all_external_services):
        """Тест оновлення неіснуючого контакту"""
        update_data = {"first_name": "Оновлене"}
        
        response = client.put("/api/v1/contacts/99999", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_contact_not_owner(self, client, create_test_contact, db_session, mock_all_external_services):
        """Тест оновлення чужого контакту"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash, create_access_token
        from datetime import timedelta
        
        # Створюємо другого користувача
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        token = create_access_token(
            data={"sub": other_user.email, "role": other_user.role.value},
            expires_delta=timedelta(minutes=30)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {"first_name": "Хакер"}
        
        response = client.put(f"/api/v1/contacts/{create_test_contact.id}", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_contact_success(self, client, auth_headers, create_test_contact, mock_all_external_services):
        """Тест успішного видалення контакту"""
        contact_id = create_test_contact.id
        
        response = client.delete(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]
        
        # Перевіряємо, що контакт дійсно видалений
        get_response = client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_contact_not_found(self, client, auth_headers, mock_all_external_services):
        """Тест видалення неіснуючого контакту"""
        response = client.delete("/api/v1/contacts/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_contact_not_owner(self, client, create_test_contact, db_session, mock_all_external_services):
        """Тест видалення чужого контакту"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash, create_access_token
        from datetime import timedelta
        
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        token = create_access_token(
            data={"sub": other_user.email, "role": other_user.role.value},
            expires_delta=timedelta(minutes=30)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/api/v1/contacts/{create_test_contact.id}", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_upcoming_birthdays_empty(self, client, auth_headers, mock_all_external_services):
        """Тест отримання порожнього списку днів народження"""
        response = client.get("/api/v1/contacts/birthdays/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_upcoming_birthdays_with_data(self, client, auth_headers, create_test_user, db_session, mock_all_external_services):
        """Тест отримання днів народження з даними"""
        from app.models.contacts import Contact
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=6)
        far_future = today + timedelta(days=30)
        
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
        
        db_session.add_all([contact_tomorrow, contact_next_week, contact_far_future])
        db_session.commit()
        
        response = client.get("/api/v1/contacts/birthdays/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # Тільки завтра та наступний тиждень
        
        emails = {contact["email"] for contact in data}
        assert "tomorrow@example.com" in emails
        assert "nextweek@example.com" in emails
        assert "future@example.com" not in emails


@pytest.mark.integration
@pytest.mark.api
class TestContactsAPIFlow:
    """Тести для комплексних scenarios з контактами"""
    
    def test_complete_contact_lifecycle(self, client, auth_headers, test_data_factory, mock_all_external_services):
        """Тест повного життєвого циклу контакту"""
        # 1. Створення контакту
        contact_data = test_data_factory.create_contact_data()
        
        create_response = client.post("/api/v1/contacts/", json=contact_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_contact = create_response.json()
        contact_id = created_contact["id"]
        
        # 2. Отримання контакту за ID
        get_response = client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["id"] == contact_id
        
        # 3. Оновлення контакту
        update_data = {
            "first_name": "Оновлене",
            "additional_data": "Нові дані"
        }
        
        update_response = client.put(f"/api/v1/contacts/{contact_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == status.HTTP_200_OK
        updated_contact = update_response.json()
        assert updated_contact["first_name"] == "Оновлене"
        assert updated_contact["additional_data"] == "Нові дані"
        
        # 4. Перевірка в загальному списку
        list_response = client.get("/api/v1/contacts/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        contacts_list = list_response.json()
        assert len(contacts_list) == 1
        assert contacts_list[0]["id"] == contact_id
        assert contacts_list[0]["first_name"] == "Оновлене"
        
        # 5. Видалення контакту
        delete_response = client.delete(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # 6. Перевірка, що контакт видалений
        final_get_response = client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
        
        final_list_response = client.get("/api/v1/contacts/", headers=auth_headers)
        assert final_list_response.status_code == status.HTTP_200_OK
        assert len(final_list_response.json()) == 0
    
    def test_multiple_users_isolation(self, client, db_session, mock_all_external_services):
        """Тест ізоляції контактів між користувачами"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash, create_access_token
        from datetime import timedelta
        
        # Створюємо двох користувачів
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=True
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=True
        )
        
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        
        # Створюємо токени
        token1 = create_access_token(
            data={"sub": user1.email, "role": user1.role.value},
            expires_delta=timedelta(minutes=30)
        )
        token2 = create_access_token(
            data={"sub": user2.email, "role": user2.role.value},
            expires_delta=timedelta(minutes=30)
        )
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Користувач 1 створює контакт
        contact1_data = {
            "first_name": "Контакт",
            "last_name": "Першого",
            "email": "contact1@example.com",
            "phone_number": "+380501234567",
            "birth_date": "1990-05-15"
        }
        
        response = client.post("/api/v1/contacts/", json=contact1_data, headers=headers1)
        assert response.status_code == status.HTTP_201_CREATED
        contact1_id = response.json()["id"]
        
        # Користувач 2 створює контакт
        contact2_data = {
            "first_name": "Контакт",
            "last_name": "Другого",
            "email": "contact2@example.com",
            "phone_number": "+380671234567",
            "birth_date": "1985-12-25"
        }
        
        response = client.post("/api/v1/contacts/", json=contact2_data, headers=headers2)
        assert response.status_code == status.HTTP_201_CREATED
        contact2_id = response.json()["id"]
        
        # Перевіряємо ізоляцію: кожен користувач бачить тільки свої контакти
        user1_contacts = client.get("/api/v1/contacts/", headers=headers1).json()
        user2_contacts = client.get("/api/v1/contacts/", headers=headers2).json()
        
        assert len(user1_contacts) == 1
        assert len(user2_contacts) == 1
        assert user1_contacts[0]["id"] == contact1_id
        assert user2_contacts[0]["id"] == contact2_id
        
        # Користувач 1 не може отримати контакт користувача 2
        response = client.get(f"/api/v1/contacts/{contact2_id}", headers=headers1)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Користувач 2 не може отримати контакт користувача 1
        response = client.get(f"/api/v1/contacts/{contact1_id}", headers=headers2)
        assert response.status_code == status.HTTP_404_NOT_FOUND