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
