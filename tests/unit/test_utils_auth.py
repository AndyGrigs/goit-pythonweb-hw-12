import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    generate_verification_token,
    generate_reset_password_token,
    create_reset_password_token,
    verify_reset_password_token
)
from app.config import settings


@pytest.mark.unit
class TestAuthUtils:
    """Тести для утиліт аутентифікації"""
    
    def test_get_password_hash(self):
        """Тест хешування пароля"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password  # Хеш не дорівнює оригінальному паролю
        assert len(hashed) > 0
        assert hashed.startswith('$2b$')  # bcrypt хеш
    
    def test_verify_password_correct(self):
        """Тест перевірки правильного пароля"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Тест перевірки неправильного пароля"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """Тест перевірки порожнього пароля"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_create_access_token_default_expiry(self):
        """Тест створення JWT токена з дефолтним часом закінчення"""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Декодуємо токен для перевірки
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "user"
        assert "exp" in payload
    
    def test_create_access_token_custom_expiry(self):
        """Тест створення JWT токена з кастомним часом закінчення"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        
        token = create_access_token(data, expires_delta)
        
        # Перевіряємо, що токен створений
        assert isinstance(token, str)
        
        # Декодуємо та перевіряємо час закінчення
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        
        # Час закінчення має бути приблизно через 60 хвилин
        expected_exp = datetime.utcnow() + expires_delta
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5  # Дозволяємо різницю до 5 секунд
    
    def test_verify_token_valid(self):
        """Тест верифікації валідного токена"""
        email = "test@example.com"
        data = {"sub": email}
        token = create_access_token(data)
        
        verified_email = verify_token(token)
        assert verified_email == email
    
    def test_verify_token_invalid_signature(self):
        """Тест верифікації токена з неправильним підписом"""
        data = {"sub": "test@example.com"}
        # Створюємо токен з неправильним ключем
        wrong_token = jwt.encode(data, "wrong_secret_key", algorithm="HS256")
        
        verified_email = verify_token(wrong_token)
        assert verified_email is None
    
    def test_verify_token_expired(self):
        """Тест верифікації прострочених токена"""
        data = {"sub": "test@example.com"}
        # Створюємо токен який закінчився годину тому
        expires_delta = timedelta(hours=-1)
        expired_token = create_access_token(data, expires_delta)
        
        verified_email = verify_token(expired_token)
        assert verified_email is None
    
    def test_verify_token_malformed(self):
        """Тест верифікації некоректного токена"""
        malformed_token = "not.a.valid.jwt.token"
        
        verified_email = verify_token(malformed_token)
        assert verified_email is None
    
    def test_verify_token_no_sub_claim(self):
        """Тест верифікації токена без sub claim"""
        data = {"role": "user"}  # Немає "sub"
        token = create_access_token(data)
        
        verified_email = verify_token(token)
        assert verified_email is None
    
    def test_generate_verification_token(self):
        """Тест генерації токена верифікації"""
        token1 = generate_verification_token()
        token2 = generate_verification_token()
        
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        assert len(token1) > 0
        assert len(token2) > 0
        assert token1 != token2  # Токени мають бути різними
    
    def test_generate_reset_password_token(self):
        """Тест генерації токена скидання пароля"""
        token1 = generate_reset_password_token()
        token2 = generate_reset_password_token()
        
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        assert len(token1) > 0
        assert len(token2) > 0
        assert token1 != token2  # Токени мають бути різними
    
    def test_create_reset_password_token_default_expiry(self):
        """Тест створення JWT токена для скидання пароля з дефолтним часом"""
        email = "test@example.com"
        token = create_reset_password_token(email)
        
        assert isinstance(token, str)
        
        # Декодуємо токен
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == email
        assert payload["type"] == "password_reset"
        assert "exp" in payload
        
        # Перевіряємо, що час закінчення приблизно через 1 годину
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        expected_exp = datetime.utcnow() + timedelta(hours=1)
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 60  # Дозволяємо різницю до 1 хвилини
    
    def test_create_reset_password_token_custom_expiry(self):
        """Тест створення JWT токена для скидання пароля з кастомним часом"""
        email = "test@example.com"
        expires_delta = timedelta(minutes=30)
        token = create_reset_password_token(email, expires_delta)
        
        # Декодуємо та перевіряємо
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == email
        assert payload["type"] == "password_reset"
        
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        expected_exp = datetime.utcnow() + expires_delta
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5
    
    def test_verify_reset_password_token_valid(self):
        """Тест верифікації валідного токена скидання пароля"""
        email = "test@example.com"
        token = create_reset_password_token(email)
        
        verified_email = verify_reset_password_token(token)
        assert verified_email == email
    
    def test_verify_reset_password_token_wrong_type(self):
        """Тест верифікації токена з неправильним типом"""
        email = "test@example.com"
        # Створюємо звичайний access token замість reset token
        data = {"sub": email, "type": "access"}
        token = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
        
        verified_email = verify_reset_password_token(token)
        assert verified_email is None
    
    def test_verify_reset_password_token_no_type(self):
        """Тест верифікації токена без типу"""
        email = "test@example.com"
        data = {"sub": email}  # Немає "type"
        token = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
        
        verified_email = verify_reset_password_token(token)
        assert verified_email is None
    
    def test_verify_reset_password_token_expired(self):
        """Тест верифікації прострочених токена скидання пароля"""
        email = "test@example.com"
        expires_delta = timedelta(hours=-1)  # Прострочений
        token = create_reset_password_token(email, expires_delta)
        
        verified_email = verify_reset_password_token(token)
        assert verified_email is None
    
    def test_verify_reset_password_token_invalid(self):
        """Тест верифікації некоректного токена скидання пароля"""
        invalid_token = "invalid.token.here"
        
        verified_email = verify_reset_password_token(invalid_token)
        assert verified_email is None
    
    def test_password_hash_different_each_time(self):
        """Тест що кожне хешування дає різний результат (через salt)"""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Хеші мають бути різними через salt
        # Але обидва мають перевірятися як правильні
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True