"""
CRUD операції для управління користувачами.

Цей модуль містить функції для створення, читання, оновлення та видалення
користувачів в системі управління контактами.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.users import User
from app.schemas.users import UserCreate, UserRoleUpdate, UserUpdate
from app.utils.auth import get_password_hash, verify_password, generate_verification_token
from datetime import datetime, timedelta

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.utils.auth import verify_token
from app.models.users import User, UserRole
from app.services.redis import redis_service
from app.services.cache_utils import invalidate_user_cache
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def user_dict_to_model(user_data: dict) -> User:
    """
    Конвертує словник в модель User.
    
    Args:
        user_data (dict): Словник з даними користувача
        
    Returns:
        User: Об'єкт моделі користувача
        
    Example:
        >>> user_data = {'id': 1, 'email': 'test@example.com', 'role': 'user'}
        >>> user = user_dict_to_model(user_data)
        >>> user.email
        'test@example.com'
    """
    user = User()
    for key, value in user_data.items():
        if key == 'role':
            # Конвертуємо строку назад в enum
            value = UserRole(value) if isinstance(value, str) else value
        setattr(user, key, value)
    return user

def user_model_to_dict(user: User) -> dict:
    """
    Конвертує модель User в словник для кешування.
    
    Args:
        user (User): Об'єкт моделі користувача
        
    Returns:
        dict: Словник з даними користувача
        
    Example:
        >>> user = User(id=1, email='test@example.com')
        >>> user_dict = user_model_to_dict(user)
        >>> user_dict['email']
        'test@example.com'
    """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'hashed_password': user.hashed_password,
        'avatar_url': user.avatar_url,
        'role': user.role.value if user.role else None,
        'is_verified': user.is_verified,
        'verification_token': user.verification_token,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Отримує поточного користувача з JWT токена (з кешуванням).
    
    Args:
        credentials (HTTPAuthorizationCredentials): JWT токен
        db (Session): Сесія бази даних
        
    Returns:
        User: Об'єкт поточного користувача
        
    Raises:
        HTTPException: 401 якщо токен невалідний або користувач не знайдений
        
    Example:
        >>> user = get_current_user(credentials, db)
        >>> user.email
        'user@example.com'
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        email = verify_token(credentials.credentials)
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    # Спробуємо отримати користувача з кешу
    cached_user_data = redis_service.get_user_cache(email)
    if cached_user_data:
        logger.debug(f"User {email} loaded from cache")
        return user_dict_to_model(cached_user_data)
    
    # Якщо немає в кеші, отримуємо з бази даних
    logger.debug(f"User {email} not in cache, loading from database")
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    # Кешуємо користувача
    user_data = user_model_to_dict(user)
    cache_success = redis_service.set_user_cache(email, user_data)
    if cache_success:
        logger.debug(f"User {email} cached successfully")
    else:
        logger.warning(f"Failed to cache user {email}")
    
    return user

def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Отримує тільки верифікованого користувача.
    
    Args:
        current_user (User): Поточний користувач
        
    Returns:
        User: Верифікований користувач
        
    Raises:
        HTTPException: 400 якщо користувач не верифікований
        
    Example:
        >>> user = get_current_verified_user(current_user)
        >>> user.is_verified
        True
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """
    Отримує тільки користувача з роллю admin.
    
    Args:
        current_user (User): Поточний верифікований користувач
        
    Returns:
        User: Користувач-адміністратор
        
    Raises:
        HTTPException: 403 якщо користувач не має роль admin
        
    Example:
        >>> admin = get_current_admin_user(current_user)
        >>> admin.role
        <UserRole.ADMIN: 'admin'>
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_role(required_role: UserRole):
    """
    Декоратор для перевірки ролі користувача.
    
    Args:
        required_role (UserRole): Необхідна роль користувача
        
    Returns:
        callable: Функція перевірки ролі
        
    Example:
        >>> @require_role(UserRole.ADMIN)
        >>> def admin_function(user):
        ...     return "Admin access granted"
    """
    def role_checker(current_user: User = Depends(get_current_verified_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' required"
            )
        return current_user
    return role_checker

def invalidate_user_cache(user_email: str):
    """
    Інвалідує кеш користувача (для використання після оновлень).
    
    Args:
        user_email (str): Email користувача
        
    Example:
        >>> invalidate_user_cache('user@example.com')
    """
    redis_service.delete_user_cache(user_email)
    logger.debug(f"Cache invalidated for user {user_email}")

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Отримує користувача за email адресою.
    
    Args:
        db (Session): Сесія бази даних
        email (str): Email адреса користувача
        
    Returns:
        Optional[User]: Користувач або None якщо не знайдено
        
    Example:
        >>> user = get_user_by_email(db, 'user@example.com')
        >>> user.email if user else None
        'user@example.com'
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Отримує користувача за іменем користувача.
    
    Args:
        db (Session): Сесія бази даних
        username (str): Ім'я користувача
        
    Returns:
        Optional[User]: Користувач або None якщо не знайдено
        
    Example:
        >>> user = get_user_by_username(db, 'testuser')
        >>> user.username if user else None
        'testuser'
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Отримує користувача за ID.
    
    Args:
        db (Session): Сесія бази даних
        user_id (int): ID користувача
        
    Returns:
        Optional[User]: Користувач або None якщо не знайдено
        
    Example:
        >>> user = get_user_by_id(db, 1)
        >>> user.id if user else None
        1
    """
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Отримує всіх користувачів (тільки для адмінів).
    
    Args:
        db (Session): Сесія бази даних
        skip (int): Кількість записів для пропуску
        limit (int): Максимальна кількість записів
        
    Returns:
        List[User]: Список користувачів
        
    Example:
        >>> users = get_all_users(db, skip=0, limit=10)
        >>> len(users)
        5
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Створює нового користувача в системі.
    
    Args:
        db (Session): Сесія бази даних
        user (UserCreate): Дані нового користувача
        
    Returns:
        User: Створений користувач
        
    Example:
        >>> user_data = UserCreate(
        ...     username='newuser',
        ...     email='new@example.com',
        ...     password='password123'
        ... )
        >>> new_user = create_user(db, user_data)
        >>> new_user.email
        'new@example.com'
    """
    hashed_password = get_password_hash(user.password)
    verification_token = generate_verification_token()
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        verification_token=verification_token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Аутентифікує користувача за email та паролем.
    
    Args:
        db (Session): Сесія бази даних
        email (str): Email користувача
        password (str): Пароль користувача
        
    Returns:
        Optional[User]: Користувач якщо аутентифікація успішна, інакше None
        
    Example:
        >>> user = authenticate_user(db, 'user@example.com', 'password123')
        >>> user.email if user else None
        'user@example.com'
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_user_email(db: Session, token: str) -> bool:
    """
    Верифікує email користувача за токеном.
    
    Args:
        db (Session): Сесія бази даних
        token (str): Токен верифікації
        
    Returns:
        bool: True якщо верифікація успішна, False інакше
        
    Example:
        >>> success = verify_user_email(db, 'verification_token_123')
        >>> success
        True
    """
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        return False
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return True

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    Оновлює дані користувача.
    
    Args:
        db (Session): Сесія бази даних
        user_id (int): ID користувача
        user_update (UserUpdate): Нові дані користувача
        
    Returns:
        Optional[User]: Оновлений користувач або None якщо не знайдено
        
    Example:
        >>> update_data = UserUpdate(username='newusername')
        >>> updated_user = update_user(db, 1, update_data)
        >>> updated_user.username if updated_user else None
        'newusername'
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def update_user_role(db: Session, user_id: int, role_update: UserRoleUpdate) -> Optional[User]:
    """
    Оновлює роль користувача (тільки для адмінів).
    
    Args:
        db (Session): Сесія бази даних
        user_id (int): ID користувача
        role_update (UserRoleUpdate): Нова роль користувача
        
    Returns:
        Optional[User]: Користувач з оновленою роллю або None якщо не знайдено
        
    Example:
        >>> role_data = UserRoleUpdate(role=UserRole.ADMIN)
        >>> updated_user = update_user_role(db, 1, role_data)
        >>> updated_user.role if updated_user else None
        <UserRole.ADMIN: 'admin'>
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> Optional[User]:
    """
    Оновлює аватар користувача.
    
    Args:
        db (Session): Сесія бази даних
        user_id (int): ID користувача
        avatar_url (str): URL нового аватара
        
    Returns:
        Optional[User]: Користувач з оновленим аватаром або None якщо не знайдено
        
    Example:
        >>> updated_user = update_user_avatar(db, 1, 'https://example.com/avatar.jpg')
        >>> updated_user.avatar_url if updated_user else None
        'https://example.com/avatar.jpg'
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user

def create_password_reset_token(db: Session, email: str) -> Optional[User]:
    """
    Створює токен для скидання пароля.
    
    Args:
        db (Session): Сесія бази даних
        email (str): Email користувача
        
    Returns:
        Optional[User]: Користувач з токеном скидання або None якщо не знайдено
        
    Example:
        >>> user = create_password_reset_token(db, 'user@example.com')
        >>> user.reset_password_token is not None if user else False
        True
    """
    from app.utils.auth import generate_reset_password_token
    
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Генеруємо токен та встановлюємо час закінчення (1 година)
    reset_token = generate_reset_password_token()
    expires_at = datetime.now(datetime.timezone.utc()) + timedelta(hours=1)
    
    user.reset_password_token = reset_token
    user.reset_password_expires = expires_at
    
    db.commit()
    db.refresh(user)
    return user

def reset_user_password(db: Session, token: str, new_password: str) -> Optional[User]:
    """
    Скидає пароль користувача за токеном.
    
    Args:
        db (Session): Сесія бази даних
        token (str): Токен скидання пароля
        new_password (str): Новий пароль
        
    Returns:
        Optional[User]: Користувач з оновленим паролем або None якщо токен невалідний
        
    Example:
        >>> user = reset_user_password(db, 'reset_token_123', 'newpassword')
        >>> user.reset_password_token is None if user else False
        True
    """
    user = db.query(User).filter(
        User.reset_password_token == token,
        User.reset_password_expires > datetime.utcnow()
    ).first()
    
    if not user:
        return None
    
    # Оновлюємо пароль та очищаємо токен
    user.hashed_password = get_password_hash(new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    
    db.commit()
    db.refresh(user)
    return user

def verify_reset_token(db: Session, token: str) -> Optional[User]:
    """
    Перевіряє валідність токена скидання пароля.
    
    Args:
        db (Session): Сесія бази даних
        token (str): Токен скидання пароля
        
    Returns:
        Optional[User]: Користувач якщо токен валідний, інакше None
        
    Example:
        >>> user = verify_reset_token(db, 'reset_token_123')
        >>> user.email if user else None
        'user@example.com'
    """
    return db.query(User).filter(
        User.reset_password_token == token,
        User.reset_password_expires > datetime.utcnow()
    ).first()