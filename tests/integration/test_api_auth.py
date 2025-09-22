import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.auth
class TestAuthAPI:
    """Інтеграційні тести для API аутентифікації"""
    
    def test_register_success(self, client, mock_all_external_services):
        """Тест успішної реєстрації користувача"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["role"] == "user"  # Дефолтна роль
        assert data["is_verified"] is False
        assert "password" not in data  # Пароль не має повертатися
    
    def test_register_duplicate_email(self, client, create_test_user, mock_all_external_services):
        """Тест реєстрації з існуючим email"""
        user_data = {
            "username": "newuser",
            "email": create_test_user.email,  # Існуючий email
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already registered" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client, create_test_user, mock_all_external_services):
        """Тест реєстрації з існуючим username"""
        user_data = {
            "username": create_test_user.username,  # Існуючий username
            "email": "newemail@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already taken" in response.json()["detail"]
    
    def test_register_invalid_email(self, client, mock_all_external_services):
        """Тест реєстрації з невалідним email"""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client, mock_all_external_services):
        """Тест реєстрації з коротким паролем"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "123"  # Занадто короткий
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_admin_role_blocked(self, client, mock_all_external_services):
        """Тест що спроба реєстрації з роллю admin блокується"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "role": "admin"  # Спроба стати адміністратором
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["role"] == "user"  # Роль змінена на user
    
    def test_register_admin_endpoint(self, client, mock_all_external_services):
        """Тест реєстрації адміністратора через спеціальний endpoint"""
        user_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "adminpassword123"
        }
        
        response = client.post("/api/v1/auth/register-admin", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["role"] == "admin"
    
    def test_login_success(self, client, create_test_user, test_user_data, mock_all_external_services):
        """Тест успішного входу"""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_email(self, client, create_test_user, mock_all_external_services):
        """Тест входу з неправильним email"""
        login_data = {
            "email": "wrong@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_wrong_password(self, client, create_test_user, mock_all_external_services):
        """Тест входу з неправильним паролем"""
        login_data = {
            "email": create_test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_unverified_user(self, client, db_session, mock_all_external_services):
        """Тест входу неверифікованого користувача"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash
        
        # Створюємо неверифікованого користувача
        unverified_user = User(
            username="unverified",
            email="unverified@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=False,
            verification_token="some_token"
        )
        db_session.add(unverified_user)
        db_session.commit()
        
        login_data = {
            "email": "unverified@example.com",
            "password": "password123"
        }
        
        # Логін повинен працювати навіть для неверифікованих користувачів
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
    
    def test_verify_email_success(self, client, db_session, mock_all_external_services):
        """Тест успішної верифікації email"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash
        
        # Створюємо користувача з токеном верифікації
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=False,
            verification_token="valid_token_123"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.get("/api/v1/auth/verify-email?token=valid_token_123")
        
        assert response.status_code == status.HTTP_200_OK
        assert "verified successfully" in response.json()["message"]
        
        # Перевіряємо, що користувач тепер верифікований
        db_session.refresh(user)
        assert user.is_verified is True
        assert user.verification_token is None
    
    def test_verify_email_invalid_token(self, client, mock_all_external_services):
        """Тест верифікації email з невалідним токеном"""
        response = client.get("/api/v1/auth/verify-email?token=invalid_token")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.json()["detail"]
    
    def test_resend_verification_existing_unverified_user(self, client, db_session, mock_all_external_services):
        """Тест повторної відправки верифікації для існуючого неверифікованого користувача"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=False,
            verification_token="some_token"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/api/v1/auth/resend-verification?email=test@example.com")
        
        assert response.status_code == status.HTTP_200_OK
        assert "verification email has been sent" in response.json()["message"]
    
    def test_resend_verification_already_verified(self, client, create_test_user, mock_all_external_services):
        """Тест повторної відправки верифікації для вже верифікованого користувача"""
        response = client.post(f"/api/v1/auth/resend-verification?email={create_test_user.email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already verified" in response.json()["detail"]
    
    def test_resend_verification_nonexistent_user(self, client, mock_all_external_services):
        """Тест повторної відправки верифікації для неіснуючого користувача"""
        response = client.post("/api/v1/auth/resend-verification?email=nonexistent@example.com")
        
        # З міркувань безпеки, завжди повертаємо успішну відповідь
        assert response.status_code == status.HTTP_200_OK
        assert "verification email has been sent" in response.json()["message"]
    
    def test_forgot_password_existing_user(self, client, create_test_user, mock_all_external_services):
        """Тест запиту скидання пароля для існуючого користувача"""
        request_data = {"email": create_test_user.email}
        
        response = client.post("/api/v1/auth/forgot-password", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "password reset link has been sent" in response.json()["message"]
    
    def test_forgot_password_nonexistent_user(self, client, mock_all_external_services):
        """Тест запиту скидання пароля для неіснуючого користувача"""
        request_data = {"email": "nonexistent@example.com"}
        
        response = client.post("/api/v1/auth/forgot-password", json=request_data)
        
        # З міркувань безпеки, завжди повертаємо успішну відповідь
        assert response.status_code == status.HTTP_200_OK
        assert "password reset link has been sent" in response.json()["message"]
    
    def test_reset_password_valid_token(self, client, db_session, create_test_user, mock_all_external_services):
        """Тест скидання пароля з валідним токеном"""
        from datetime import datetime, timedelta
        
        # Встановлюємо токен скидання пароля
        reset_token = "valid_reset_token_123"
        expires_at = datetime.now(datetime.timezone.utc()) + timedelta(hours=1)
        
        create_test_user.reset_password_token = reset_token
        create_test_user.reset_password_expires = expires_at
        db_session.commit()
        
        reset_data = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "reset successfully" in response.json()["message"]
        
        # Перевіряємо, що токен очищений
        db_session.refresh(create_test_user)
        assert create_test_user.reset_password_token is None
        assert create_test_user.reset_password_expires is None
    
    def test_reset_password_invalid_token(self, client, mock_all_external_services):
        """Тест скидання пароля з невалідним токеном"""
        reset_data = {
            "token": "invalid_token",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.json()["detail"]
    
    def test_reset_password_expired_token(self, client, db_session, create_test_user, mock_all_external_services):
        """Тест скидання пароля з простроченим токеном"""
        from datetime import datetime, timedelta
        
        # Встановлюємо прострочений токен
        reset_token = "expired_token_123"
        expires_at = datetime.now(datetime.timezone.utc()) - timedelta(hours=1)
        
        create_test_user.reset_password_token = reset_token
        create_test_user.reset_password_expires = expires_at
        db_session.commit()
        
        reset_data = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.json()["detail"]
    
    def test_verify_reset_token_valid(self, client, db_session, create_test_user, mock_all_external_services):
        """Тест перевірки валідного токена скидання пароля"""
        from datetime import datetime, timedelta
        
        reset_token = "valid_token_123"
        expires_at = datetime.now(datetime.timezone.utc()) + timedelta(hours=1)
        
        create_test_user.reset_password_token = reset_token
        create_test_user.reset_password_expires = expires_at
        db_session.commit()
        
        response = client.get(f"/api/v1/auth/verify-reset-token?token={reset_token}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Token is valid" in data["message"]
        assert data["email"] == create_test_user.email
    
    def test_verify_reset_token_invalid(self, client, mock_all_external_services):
        """Тест перевірки невалідного токена скидання пароля"""
        response = client.get("/api/v1/auth/verify-reset-token?token=invalid_token")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.json()["detail"]
    
    def test_register_missing_fields(self, client, mock_all_external_services):
        """Тест реєстрації з відсутніми полями"""
        incomplete_data = {
            "username": "testuser"
            # Відсутні email та password
        }
        
        response = client.post("/api/v1/auth/register", json=incomplete_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_fields(self, client, mock_all_external_services):
        """Тест входу з відсутніми полями"""
        incomplete_data = {
            "email": "test@example.com"
            # Відсутній password
        }
        
        response = client.post("/api/v1/auth/login", json=incomplete_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_forgot_password_invalid_email_format(self, client, mock_all_external_services):
        """Тест запиту скидання пароля з невалідним форматом email"""
        request_data = {"email": "not-an-email"}
        
        response = client.post("/api/v1/auth/forgot-password", json=request_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_reset_password_short_password(self, client, mock_all_external_services):
        """Тест скидання пароля з занадто коротким паролем"""
        reset_data = {
            "token": "some_token",
            "new_password": "123"  # Занадто короткий
        }
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
@pytest.mark.auth
class TestAuthAPIFlow:
    """Тести для повного flow аутентифікації"""
    
    def test_complete_registration_and_login_flow(self, client, mock_all_external_services):
        """Тест повного циклу: реєстрація -> верифікація -> вхід"""
        # 1. Реєстрація
        user_data = {
            "username": "flowuser",
            "email": "flowuser@example.com",
            "password": "password123"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # 2. Спроба входу до верифікації (має працювати)
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        # 3. Верифікація email (симулюємо)
        # У реальності токен прийшов би в email, тут симулюємо його знаходження
        from app.models.users import User
        from app.database.connection import SessionLocal
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            token = user.verification_token
        finally:
            db.close()
        
        verify_response = client.get(f"/api/v1/auth/verify-email?token={token}")
        assert verify_response.status_code == status.HTTP_200_OK
        
        # 4. Повторний вхід після верифікації
        final_login_response = client.post("/api/v1/auth/login", json=login_data)
        assert final_login_response.status_code == status.HTTP_200_OK
    
    def test_complete_password_reset_flow(self, client, create_test_user, mock_all_external_services):
        """Тест повного циклу скидання пароля"""
        # 1. Запит скидання пароля
        request_data = {"email": create_test_user.email}
        
        forgot_response = client.post("/api/v1/auth/forgot-password", json=request_data)
        assert forgot_response.status_code == status.HTTP_200_OK
        
        # 2. Отримуємо токен скидання з бази
        from app.database.connection import SessionLocal
        
        db = SessionLocal()
        try:
            db.refresh(create_test_user)
            reset_token = create_test_user.reset_password_token
        finally:
            db.close()
        
        assert reset_token is not None
        
        # 3. Перевіряємо токен
        verify_response = client.get(f"/api/v1/auth/verify-reset-token?token={reset_token}")
        assert verify_response.status_code == status.HTTP_200_OK
        
        # 4. Скидаємо пароль
        reset_data = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        
        reset_response = client.post("/api/v1/auth/reset-password", json=reset_data)
        assert reset_response.status_code == status.HTTP_200_OK
        
        # 5. Входимо з новим паролем
        login_data = {
            "email": create_test_user.email,
            "password": "newpassword123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        # 6. Перевіряємо, що старий пароль не працює
        old_login_data = {
            "email": create_test_user.email,
            "password": "testpassword123"  # Старий пароль
        }
        
        old_login_response = client.post("/api/v1/auth/login", json=old_login_data)
        assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED