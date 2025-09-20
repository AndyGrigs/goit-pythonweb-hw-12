from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.utils.auth import verify_token
from app.crud.users import get_user_by_email
from app.models.users import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Отримання поточного користувача з JWT токена"""
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
        
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
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