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
from app.crud.users import get_user_by_email
from app.models.users import User, UserRole
from app.services.redis import redis_service
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def user_dict_to_model(user_data: dict) -> User:
    """Конвертація словника в модель User"""
    user = User()
    for key, value in user_data.items():
        if key == 'role':
            # Конвертуємо строку назад в enum
            value = UserRole(value) if isinstance(value, str) else value
        setattr(user, key, value)
    return user

def user_model_to_dict(user: User) -> dict:
    """Конвертація моделі User в словник для кешування"""
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
    """Отримання поточного користувача з JWT токена (з кешуванням)"""
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
    """Отримання тільки верифікованого користувача"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Отримання тільки користувача з роллю admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_role(required_role: UserRole):
    """Декоратор для перевірки ролі користувача"""
    def role_checker(current_user: User = Depends(get_current_verified_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' required"
            )
        return current_user
    return role_checker

def invalidate_user_cache(user_email: str):
    """Функція для інвалідації кешу користувача (для використання після оновлень)"""
    redis_service.delete_user_cache(user_email)
    logger.debug(f"Cache invalidated for user {user_email}")

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Отримання користувача за email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Отримання користувача за username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Отримання користувача за ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Отримання всіх користувачів (тільки для адмінів)"""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """Створення нового користувача"""
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
    """Аутентифікація користувача"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_user_email(db: Session, token: str) -> bool:
    """Верифікація email користувача"""
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        return False
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return True

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Оновлення користувача"""
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
    """Оновлення ролі користувача (тільки для адмінів)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> Optional[User]:
    """Оновлення аватара користувача"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user

def create_password_reset_token(db: Session, email: str) -> Optional[User]:
    """Створення токена для скидання пароля"""
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
    """Скидання пароля користувача за токеном"""
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
    """Перевірка валідності токена скидання пароля"""
    return db.query(User).filter(
        User.reset_password_token == token,
        User.reset_password_expires > datetime.utcnow()
    ).first()