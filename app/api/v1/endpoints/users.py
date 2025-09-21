from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.middleware.auth import (
    get_current_verified_user, 
    get_current_admin_user
)
from app.middleware.rate_limiter import limiter, get_rate_limit_for_me
from app.schemas.users import UserResponse, UserUpdate, UserRoleUpdate
from app.crud.users import (
    update_user, 
    update_user_avatar, 
    update_user_role,
    get_all_users,
    get_user_by_id
)
from app.models.users import User, UserRole


router = APIRouter()

@router.get("/me", response_model=UserResponse)
@limiter.limit(get_rate_limit_for_me())
def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_verified_user)
):
    """Отримання інформації про поточного користувача (з rate limiting)"""
    return current_user


# === Маршрути ТІЛЬКИ ДЛЯ АДМІНІСТРАТОРІВ ===

@router.post("/me/avatar", response_model=UserResponse)
async def upload_user_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Тільки адміни!
):
    """Завантаження аватара користувача (тільки для адміністраторів)"""
    # Перевірка типу файлу
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Перевірка розміру файлу (макс 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum 5MB allowed"
        )
    
    try:
        # Завантаження в Cloudinary
        from app.services.cloudinary import upload_avatar
        
        filename = f"user_{current_user.id}_{file.filename}"
        avatar_url = upload_avatar(file_content, filename)
        
        # Оновлення в базі даних
        updated_user = update_user_avatar(db, current_user.id, avatar_url)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update avatar"
            )
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload avatar: {str(e)}"
        )



@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role_endpoint(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Зміна ролі користувача (тільки для адміністраторів)"""
    # Перевірка, що адмін не знижує себе
    if user_id == current_user.id and role_update.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot demote themselves"
        )
    
    updated_user = update_user_role(db, user_id, role_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user
