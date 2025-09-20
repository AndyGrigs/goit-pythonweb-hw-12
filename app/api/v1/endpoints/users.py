from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.middleware.auth import get_current_verified_user
from app.middleware.rate_limiter import limiter, get_rate_limit_for_me
from app.schemas.users import UserResponse, UserUpdate
from app.crud.users import update_user, update_user_avatar
from app.models.users import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
@limiter.limit(get_rate_limit_for_me())
def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_verified_user)
):
    """Отримання інформації про поточного користувача (з rate limiting)"""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_users_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Оновлення інформації про користувача"""
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update user"
        )
    return updated_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_user_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Завантаження аватара користувача"""
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