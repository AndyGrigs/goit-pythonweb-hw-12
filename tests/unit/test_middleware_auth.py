import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.middleware.auth import (
    get_current_user,
    get_current_verified_user,
    get_current_admin_user,
    user_dict_to_model,
    user_model_to_dict
)
from app.models.users import User, UserRole


@pytest.mark.unit
class TestAuthMiddleware:
    """Тести для middleware аутентифікації"""
    
    def test_user_model_to_dict(self, create_test_user):
        """Тест конвертації моделі User в словник"""
        user_dict = user_model_to_dict(create_test_user)
        
        assert user_dict["id"] == create_test_user.id
        assert user_dict["username"] == create_test_user.username
        assert user_dict["email"] == create_test_user.email
        assert user_dict["role"] == create_test_user.role.value
        assert user_dict["is_verified"] == create_test_user.is_verified
        assert "hashed_password" in user_dict
    
    def test_user_dict_to_model(self, create_test_user):
        """Тест конвертації словника в модель User"""
        user_dict = user_model_to_dict(create_test_user)
        reconstructed_user = user_dict_to_model(user_dict)
        
        assert reconstructed_user.id == create_test_user.id
        assert reconstructed_user.username == create_test_user.username
        assert reconstructed_user.email == create_test_user.email
        assert reconstructed_user.role == create_test_user.role
        assert reconstructed_user.is_verified == create_test_user.is_verified
    
    @patch('app.middleware.auth.verify_token')
    @patch('app.middleware.auth.redis_service')
    @patch('app.middleware.auth.get_user_by_email')
    def test_get_current_user_with_cache(self, mock_get_user_by_email, mock_redis_service, mock_verify_token, create_test_user, db_session):
        """Тест отримання поточного користувача з кешу"""
        # Налаштування мокувань
        mock_verify_token.return_value = create_test_user.email
        user_data = user_model_to_dict(create_test_user)
        mock_redis_service.get_user_cache.return_value = user_data
        
        # Створюємо фіктивні credentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        # Викликаємо функцію
        user = get_current_user(credentials, db_session)
        
        # Перевірки
        assert user.email == create_test_user.email
        assert user.id == create_test_user.id
        mock_redis_service.get_user_cache.assert_called_once_with(create_test_user.email)
        mock_get_user_by_email.assert_not_called()  # Не повинен викликатися, бо є кеш
    
    @patch('app.middleware.auth.verify_token')
    @patch('app.middleware.auth.redis_service')
    @patch('app.middleware.auth.get_user_by_email')
    def test_get_current_user_without_cache(self, mock_get_user_by_email, mock_redis_service, mock_verify_token, create_test_user, db_session):
        """Тест отримання поточного користувача без кешу"""
        # Налаштування мокувань
        mock_verify_token.return_value = create_test_user.email
        mock_redis_service.get_user_cache.return_value = None  # Немає в кеші
        mock_get_user_by_email.return_value = create_test_user
        mock_redis_service.set_user_cache.return_value = True
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        user = get_current_user(credentials, db_session)
        
        assert user.email == create_test_user.email
        mock_redis_service.get_user_cache.assert_called_once_with(create_test_user.email)
        mock_get_user_by_email.assert_called_once_with(db_session, email=create_test_user.email)
        mock_redis_service.set_user_cache.assert_called_once()
    
    @patch('app.middleware.auth.verify_token')
    def test_get_current_user_invalid_token(self, mock_verify_token, db_session):
        """Тест отримання користувача з невалідним токеном"""
        mock_verify_token.return_value = None  # Невалідний токен
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    @patch('app.middleware.auth.verify_token')
    @patch('app.middleware.auth.redis_service')
    @patch('app.middleware.auth.get_user_by_email')
    def test_get_current_user_not_found_in_db(self, mock_get_user_by_email, mock_redis_service, mock_verify_token, db_session):
        """Тест отримання користувача, якого немає в базі"""
        mock_verify_token.return_value = "nonexistent@example.com"
        mock_redis_service.get_user_cache.return_value = None
        mock_get_user_by_email.return_value = None  # Користувач не знайдений
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_verified_user_success(self, create_test_user):
        """Тест отримання верифікованого користувача"""
        create_test_user.is_verified = True
        
        user = get_current_verified_user(create_test_user)
        
        assert user == create_test_user
    
    def test_get_current_verified_user_not_verified(self, create_test_user):
        """Тест отримання неверифікованого користувача"""
        create_test_user.is_verified = False
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_verified_user(create_test_user)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "not verified" in str(exc_info.value.detail)
    
    def test_get_current_admin_user_success(self, create_test_admin):
        """Тест отримання користувача-адміністратора"""
        user = get_current_admin_user(create_test_admin)
        
        assert user == create_test_admin
        assert user.role == UserRole.ADMIN
    
    def test_get_current_admin_user_not_admin(self, create_test_user):
        """Тест отримання звичайного користувача замість адміна"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(create_test_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in str(exc_info.value.detail)
    
    @patch('app.middleware.auth.verify_token')
    def test_get_current_user_token_exception(self, mock_verify_token, db_session):
        """Тест обробки винятку при верифікації токена"""
        mock_verify_token.side_effect = Exception("Token verification failed")
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="problematic_token")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
class TestAuthMiddlewareWithRedis:
    """Тести для middleware з Redis"""
    
    @patch('app.middleware.auth.verify_token')
    @patch('app.middleware.auth.redis_service')
    @patch('app.middleware.auth.get_user_by_email')
    def test_redis_cache_failure_fallback_to_db(self, mock_get_user_by_email, mock_redis_service, mock_verify_token, create_test_user, db_session):
        """Тест що при збої Redis використовується база даних"""
        mock_verify_token.return_value = create_test_user.email
        mock_redis_service.get_user_cache.side_effect = Exception("Redis connection failed")
        mock_get_user_by_email.return_value = create_test_user
        mock_redis_service.set_user_cache.return_value = False  # Кешування не вдалося
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        user = get_current_user(credentials, db_session)
        
        assert user.email == create_test_user.email
        mock_get_user_by_email.assert_called_once()
    
    @patch('app.middleware.auth.verify_token')
    @patch('app.middleware.auth.redis_service')
    @patch('app.middleware.auth.get_user_by_email')
    def test_redis_set_cache_failure(self, mock_get_user_by_email, mock_redis_service, mock_verify_token, create_test_user, db_session):
        """Тест що збій кешування не впливає на роботу"""
        mock_verify_token.return_value = create_test_user.email
        mock_redis_service.get_user_cache.return_value = None
        mock_get_user_by_email.return_value = create_test_user
        mock_redis_service.set_user_cache.return_value = False  # Кешування не вдалося
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        # Функція повинна працювати навіть якщо кешування не вдалося
        user = get_current_user(credentials, db_session)
        
        assert user.email == create_test_user.email
        mock_redis_service.set_user_cache.assert_called_once()
    
    def test_user_dict_to_model_with_datetime_strings(self):
        """Тест конвертації з datetime як строками"""
        from datetime import datetime
        
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'hashed_password': 'hashed',
            'avatar_url': None,
            'role': 'user',
            'is_verified': True,
            'verification_token': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        user = user_dict_to_model(user_data)
        
        assert user.id == 1
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == UserRole.USER
        assert user.is_verified is True
    
    def test_user_dict_to_model_with_none_role(self):
        """Тест конвертації з None роллю"""
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'hashed_password': 'hashed',
            'avatar_url': None,
            'role': None,
            'is_verified': True,
            'verification_token': None,
            'created_at': None,
            'updated_at': None
        }
        
        user = user_dict_to_model(user_data)
        
        assert user.role is None