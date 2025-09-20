from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.users import UserRole

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255)
    role: Optional[UserRole] = UserRole.USER

class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    role: UserRole
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    
class EmailVerification(BaseModel):
    token: str

class UserRoleUpdate(BaseModel):
    """Окрема схема для зміни ролі користувача (тільки для адмінів)"""
    role: UserRole