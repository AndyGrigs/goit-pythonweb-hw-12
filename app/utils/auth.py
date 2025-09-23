"""
Утиліти для аутентифікації та авторизації.

Цей модуль містить функції для роботи з паролями, JWT токенами,
токенами верифікації email та скидання пароля.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
import secrets

# Контекст для хешування паролів з використанням bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Перевіряє пароль користувача.
    
    Args:
        plain_password (str): Пароль у відкритому вигляді
        hashed_password (str): Хешований пароль з бази даних
        
    Returns:
        bool: True якщо пароль правильний, False інакше
        
    Example:
        >>> hashed = get_password_hash("mypassword")
        >>> verify_password("mypassword", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хешує пароль користувача для безпечного зберігання.
    
    Args:
        password (str): Пароль у відкритому вигляді
        
    Returns:
        str: Хешований пароль
        
    Note:
        Використовує bcrypt з автоматичною генерацією salt
        
    Example:
        >>> hashed = get_password_hash("mypassword")
        >>> len(hashed) > 50
        True
        >>> hashed.startswith('$2b)
        True
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Створює JWT токен доступу.
    
    Args:
        data (dict): Дані для включення в токен (зазвичай {'sub': email})
        expires_delta (Optional[timedelta]): Час життя токена
        
    Returns:
        str: JWT токен
        
    Example:
        >>> token = create_access_token(
        ...     data={'sub': 'user@example.com', 'role': 'user'},
        ...     expires_delta=timedelta(minutes=30)
        ... )
        >>> len(token) > 100
        True
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Верифікує JWT токен та витягує email користувача.
    
    Args:
        token (str): JWT токен для верифікації
        
    Returns:
        Optional[str]: Email користувача якщо токен валідний, інакше None
        
    Example:
        >>> token = create_access_token({'sub': 'user@example.com'})
        >>> email = verify_token(token)
        >>> email
        'user@example.com'
        >>> verify_token('invalid_token')
        
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def generate_verification_token() -> str:
    """
    Генерує токен для верифікації email.
    
    Returns:
        str: Безпечний випадковий токен
        
    Note:
        Використовує криптографічно безпечний генератор випадкових чисел
        
    Example:
        >>> token = generate_verification_token()
        >>> len(token) > 30
        True
        >>> token != generate_verification_token()
        True
    """
    return secrets.token_urlsafe(32)


def generate_reset_password_token() -> str:
    """
    Генерує токен для скидання пароля.
    
    Returns:
        str: Безпечний випадковий токен
        
    Note:
        Використовує криптографічно безпечний генератор випадкових чисел
        
    Example:
        >>> token = generate_reset_password_token()
        >>> len(token) > 30
        True
        >>> token != generate_reset_password_token()
        True
    """
    return secrets.token_urlsafe(32)


def create_reset_password_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Створює JWT токен для скидання пароля.
    
    Args:
        email (str): Email користувача
        expires_delta (Optional[timedelta]): Час життя токена (за замовчуванням 1 година)
        
    Returns:
        str: JWT токен для скидання пароля
        
    Example:
        >>> token = create_reset_password_token('user@example.com')
        >>> len(token) > 100
        True
        >>> # Токен містить тип "password_reset"
        >>> from jose import jwt
        >>> payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        >>> payload['type']
        'password_reset'
    """
    to_encode = {"sub": email, "type": "password_reset"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)  # Токен дійсний 1 годину
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_reset_password_token(token: str) -> Optional[str]:
    """
    Верифікує токен скидання пароля та витягує email.
    
    Args:
        token (str): JWT токен скидання пароля
        
    Returns:
        Optional[str]: Email користувача якщо токен валідний, інакше None
        
    Note:
        Перевіряє не тільки підпис та час закінчення, а й тип токена
        
    Example:
        >>> reset_token = create_reset_password_token('user@example.com')
        >>> email = verify_reset_password_token(reset_token)
        >>> email
        'user@example.com'
        >>> # Звичайний access token не підійде
        >>> access_token = create_access_token({'sub': 'user@example.com'})
        >>> verify_reset_password_token(access_token)
        
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "password_reset":
            return None
        return email
    except JWTError:
        return None