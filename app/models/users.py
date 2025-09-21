from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    USER ="user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    # Поля для скидання пароля
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), nullable=True)
    verification_token = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Зв'язок з контактами
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
    def is_admin(self) -> bool:
        """Перевірка чи користувач є адміністратором"""
        return self.role == UserRole.ADMIN