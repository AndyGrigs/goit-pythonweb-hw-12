from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.deps import get_db
from app.schemas.users import UserCreate, UserLogin, Token, UserResponse
from app.models.users import UserRole
from app.crud.users import (
    get_user_by_email, 
    get_user_by_username,
    create_user, 
    authenticate_user,
    verify_user_email
)
from app.utils.auth import create_access_token
from app.services.email import send_verification_email
from app.config import settings
from app.schemas.users import PasswordResetRequest, PasswordResetConfirm, PasswordResetResponse
from app.crud.users import create_password_reset_token, reset_user_password, verify_reset_token
from app.services.email import send_password_reset_email

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Реєстрація нового користувача"""
    # Перевірка чи користувач вже існує
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    
    # Заборона створення адміністраторів через публічну реєстрацію
    if user.role == UserRole.ADMIN:
        user.role = UserRole.USER
    
    # Створення користувача
    db_user = create_user(db=db, user=user)
    
    # Відправка email для верифікації в фоновому режимі
    if db_user.verification_token:
        background_tasks.add_task(
            send_verification_email, 
            db_user.email, 
            db_user.verification_token
        )
    
    return db_user

@router.post("/register-admin", response_model=UserResponse, status_code=201)
async def register_admin(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Реєстрація адміністратора (спеціальний endpoint)"""
    # Перевірка чи користувач вже існує
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    
    # Примусово встановлюємо роль admin
    user.role = UserRole.ADMIN
    
    # Створення користувача-адміністратора
    db_user = create_user(db=db, user=user)
    
    # Відправка email для верифікації в фоновому режимі
    if db_user.verification_token:
        background_tasks.add_task(
            send_verification_email, 
            db_user.email, 
            db_user.verification_token
        )
    
    return db_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Вхід користувача"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Додаємо роль користувача в токен
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Верифікація email користувача"""
    if not verify_user_email(db, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification_email(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Повторна відправка email верифікації"""
    user = get_user_by_email(db, email)
    if not user:
        return {"message": "If email exists, verification email has been sent"}
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    if user.verification_token:
        background_tasks.add_task(
            send_verification_email,
            user.email,
            user.verification_token
        )
    
    return {"message": "If email exists, verification email has been sent"}

@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    password_reset: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Запит скидання пароля"""
    # Створюємо токен скидання пароля
    user = create_password_reset_token(db, password_reset.email)
    
    # Відправляємо email навіть якщо користувач не знайдений (для безпеки)
    if user and user.reset_password_token:
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            user.reset_password_token
        )
    
    # Завжди повертаємо успішну відповідь (не розкриваємо чи email існує)
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent"
    )

@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(
    password_reset: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Скидання пароля за токеном"""
    # Скидаємо пароль
    user = reset_user_password(db, password_reset.token, password_reset.new_password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return PasswordResetResponse(message="Password reset successfully")

@router.get("/verify-reset-token")
def verify_password_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Перевірка валідності токена скидання пароля"""
    user = verify_reset_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Token is valid", "email": user.email}