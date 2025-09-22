import pytest
from datetime import datetime, timedelta
from app.crud.users import (
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    create_user,
    authenticate_user,
    verify_user_email,
    update_user,
    update_user_role,
    update_user_avatar,
    create_password_reset_token,
    reset_user_password,
    verify_reset_token
)
from app.schemas.users import UserCreate, UserUpdate, UserRoleUpdate
from app.models.users import User, UserRole
from app.utils.auth import get_password_hash


@pytest.mark.unit
@pytest.mark.crud
class TestUserCRUD:
    """Тести для CRUD операцій користувачів"""
    
    def test_get_user_by_email_existing(self, db_session, create_test_user):
        """Тест отримання користувача за email (існуючий)"""
        user = get_user_by_email(db_session, create_test_user.email)
        
        assert user is not None
        assert user.email == create_test_user.email
        assert user.id == create_test_user.id
    
    def test_get_user_by_email_not_existing(self, db_session):
        """Тест отримання користувача за email (неіснуючий)"""
        user = get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None
    
    def test_get_user_by_username_existing(self, db_session, create_test_user):
        """Тест отримання користувача за username (існуючий)"""
        user = get_user_by_username(db_session, create_test_user.username)
        
        assert user is not None
        assert user.username == create_test_user.username
        assert user.id == create_test_user.id
    
    def test_get_user_by_username_not_existing(self, db_session):
        """Тест отримання користувача за username (неіснуючий)"""
        user = get_user_by_username(db_session, "nonexistent")
        assert user is None
    
    def test_get_user_by_id_existing(self, db_session, create_test_user):
        """Тест отримання користувача за ID (існуючий)"""
        user = get_user_by_id(db_session, create_test_user.id)
        
        assert user is not None
        assert user.id == create_test_user.id
        assert user.email == create_test_user.email
    
    def test_get_user_by_id_not_existing(self, db_session):
        """Тест отримання користувача за ID (неіснуючий)"""
        user = get_user_by_id(db_session, 99999)
        assert user is None
    
    def test_create_user_success(self, db_session):
        """Тест успішного створення користувача"""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            role=UserRole.USER
        )
        
        created_user = create_user(db_session, user_data)
        
        assert created_user.username == user_data.username
        assert created_user.email == user_data.email
        assert created_user.role == user_data.role
        assert created_user.is_verified is False
        assert created_user.verification_token is not None
        assert created_user.hashed_password != user_data.password  # Пароль має бути хешований
    
    def test_authenticate_user_valid_credentials(self, db_session, create_test_user, test_user_data):
        """Тест аутентифікації з валідними credentials"""
        user = authenticate_user(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        assert user is not None
        assert user.email == test_user_data["email"]
        assert user.id == create_test_user.id
    
    def test_authenticate_user_invalid_email(self, db_session):
        """Тест аутентифікації з неправильним email"""
        user = authenticate_user(db_session, "wrong@example.com", "password123")
        assert user is None
    
    def test_authenticate_user_invalid_password(self, db_session, create_test_user):
        """Тест аутентифікації з неправильним паролем"""
        user = authenticate_user(db_session, create_test_user.email, "wrongpassword")
        assert user is None
    
    def test_verify_user_email_valid_token(self, db_session):
        """Тест верифікації email з валідним токеном"""
        # Створюємо користувача з токеном верифікації
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            verification_token="valid_token_123",
            is_verified=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Верифікуємо email
        result = verify_user_email(db_session, "valid_token_123")
        
        assert result is True
        
        # Перевіряємо, що користувач верифікований
        db_session.refresh(user)
        assert user.is_verified is True
        assert user.verification_token is None
    
    def test_verify_user_email_invalid_token(self, db_session):
        """Тест верифікації email з невалідним токеном"""
        result = verify_user_email(db_session, "invalid_token")
        assert result is False
    
    def test_update_user_success(self, db_session, create_test_user):
        """Тест успішного оновлення користувача"""
        update_data = UserUpdate(username="updateduser")
        
        updated_user = update_user(db_session, create_test_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.username == "updateduser"
        assert updated_user.email == create_test_user.email  # Email не змінився
    
    def test_update_user_not_found(self, db_session):
        """Тест оновлення неіснуючого користувача"""
        update_data = UserUpdate(username="updateduser")
        
        updated_user = update_user(db_session, 99999, update_data)
        assert updated_user is None
    
    def test_update_user_role_success(self, db_session, create_test_user):
        """Тест успішного оновлення ролі користувача"""
        role_update = UserRoleUpdate(role=UserRole.ADMIN)
        
        updated_user = update_user_role(db_session, create_test_user.id, role_update)
        
        assert updated_user is not None
        assert updated_user.role == UserRole.ADMIN
    
    def test_update_user_role_not_found(self, db_session):
        """Тест оновлення ролі неіснуючого користувача"""
        role_update = UserRoleUpdate(role=UserRole.ADMIN)
        
        updated_user = update_user_role(db_session, 99999, role_update)
        assert updated_user is None
    
    def test_update_user_avatar_success(self, db_session, create_test_user):
        """Тест успішного оновлення аватара користувача"""
        avatar_url = "https://example.com/avatar.jpg"
        
        updated_user = update_user_avatar(db_session, create_test_user.id, avatar_url)
        
        assert updated_user is not None
        assert updated_user.avatar_url == avatar_url
    
    def test_update_user_avatar_not_found(self, db_session):
        """Тест оновлення аватара неіснуючого користувача"""
        avatar_url = "https://example.com/avatar.jpg"
        
        updated_user = update_user_avatar(db_session, 99999, avatar_url)
        assert updated_user is None
    
    def test_create_password_reset_token_existing_user(self, db_session, create_test_user):
        """Тест створення токена скидання пароля для існуючого користувача"""
        user = create_password_reset_token(db_session, create_test_user.email)
        
        assert user is not None
        assert user.reset_password_token is not None
        assert user.reset_password_expires is not None
        assert user.reset_password_expires > datetime.now(datetime.timezone.utc())
    
    def test_create_password_reset_token_not_existing_user(self, db_session):
        """Тест створення токена скидання пароля для неіснуючого користувача"""
        user = create_password_reset_token(db_session, "nonexistent@example.com")
        assert user is None
    
    def test_reset_user_password_valid_token(self, db_session, create_test_user):
        """Тест скидання пароля з валідним токеном"""
        # Створюємо токен скидання
        reset_token = "valid_reset_token"
        expires_at = datetime.now(datetime.timezone.utc()) + timedelta(hours=1)
        
        create_test_user.reset_password_token = reset_token
        create_test_user.reset_password_expires = expires_at
        db_session.commit()
        
        # Скидаємо пароль
        new_password = "newpassword123"
        user = reset_user_password(db_session, reset_token, new_password)
        
        assert user is not None
        assert user.reset_password_token is None
        assert user.reset_password_expires is None
        # Перевіряємо, що пароль змінився
        from app.utils.auth import verify_password
        assert verify_password(new_password, user.hashed_password)
    
    def test_reset_user_password_invalid_token(self, db_session):
        """Тест скидання пароля з невалідним токеном"""
        user = reset_user_password(db_session, "invalid_token", "newpassword123")
        assert user is None
    
    def test_reset_user_password_expired_token(self, db_session, create_test_user):
        """Тест скидання пароля з просроченим токеном"""
        # Створюємо прострочений токен
        reset_token = "expired_token"
        expires_at = datetime.now(datetime.timezone.utc()) - timedelta(hours=1)
        
        create_test_user.reset_password_token = reset_token
        create_test_user.reset_password_expires = expires_at
        db_session.commit()
        
        # Намагаємося скинути пароль
        user = reset_user_password(db_session, reset_token, "newpassword123")
        assert user is None
    
    def test_verify_reset_token_valid(self, db_session, create_test_user):
        """Тест перевірки валідного токена скидання"""
        reset_token = "valid_reset_token"
        expires_at = datetime.now(datetime.timezone.utc()) + timedelta(hours=1)
        
        create_test_user.reset_password_token = reset_token
        create_test_user.reset_password_expires = expires_at
        db_session.commit()
        
        user = verify_reset_token(db_session, reset_token)
        assert user is not None
        assert user.id == create_test_user.id
    
    def test_verify_reset_token_invalid(self, db_session):
        """Тест перевірки невалідного токена скидання"""
        user = verify_reset_token(db_session, "invalid_token")
        assert user is None