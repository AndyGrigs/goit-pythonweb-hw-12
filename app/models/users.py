"""
Моделі користувачів для системи управління контактами.

Цей модуль містить SQLAlchemy моделі та енуми для роботи з користувачами,
включаючи ролі, аутентифікацію та управління профілями.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum
from datetime import datetime


class UserRole(str, enum.Enum):
    """
    Енум для ролей користувачів в системі.
    
    Attributes:
        USER (str): Звичайний користувач з базовими правами
        ADMIN (str): Адміністратор з розширеними правами
        
    Example:
        >>> role = UserRole.USER
        >>> role.value
        'user'
        >>> UserRole.ADMIN
        <UserRole.ADMIN: 'admin'>
    """
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    Модель користувача системи управління контактами.
    
    Attributes:
        id (int): Унікальний ідентифікатор користувача
        username (str): Ім'я користувача (унікальне)
        email (str): Email адреса (унікальна)
        hashed_password (str): Хешований пароль
        reset_password_token (str, optional): Токен для скидання пароля
        reset_password_expires (datetime, optional): Час закінчення дії токена скидання
        avatar_url (str, optional): URL аватара користувача
        is_verified (bool): Чи верифікований email користувача
        role (UserRole, optional): Роль користувача в системі
        verification_token (str, optional): Токен для верифікації email
        created_at (datetime): Час створення запису
        updated_at (datetime, optional): Час останнього оновлення
        contacts (relationship): Зв'язок з контактами користувача
        
    Note:
        Всі паролі зберігаються в хешованому вигляді з використанням bcrypt.
        Токени верифікації та скидання пароля мають обмежений час дії.
        
    Example:
        >>> user = User(
        ...     username='johndoe',
        ...     email='john@example.com',
        ...     hashed_password='$2b$12$...',
        ...     role=UserRole.USER
        ... )
        >>> user.is_admin()
        False
    """
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, doc="Унікальний ідентифікатор користувача")
    username = Column(String(50), unique=True, nullable=False, index=True, 
                     doc="Ім'я користувача (унікальне, 3-50 символів)")
    email = Column(String(100), unique=True, nullable=False, index=True,
                  doc="Email адреса користувача (унікальна)")
    hashed_password = Column(String(255), nullable=False,
                           doc="Хешований пароль користувача (bcrypt)")
    
    # Поля для скидання пароля
    reset_password_token = Column(String(255), nullable=True,
                                doc="Токен для скидання пароля (тимчасовий)")
    reset_password_expires = Column(DateTime(timezone=True), nullable=True,
                                  doc="Час закінчення дії токена скидання пароля")
    
    avatar_url = Column(String(255), nullable=True,
                       doc="URL аватара користувача (Cloudinary)")
    is_verified = Column(Boolean, default=False,
                        doc="Чи верифікований email користувача")
    role = Column(Enum(UserRole), nullable=True, default=UserRole.USER,
                 doc="Роль користувача в системі")
    verification_token = Column(String(255), nullable=True,
                              doc="Токен для верифікації email адреси")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       doc="Час створення запису користувача")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                       doc="Час останнього оновлення запису")

    # Зв'язок з контактами
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan",
                          doc="Всі контакти користувача (каскадне видалення)")

    def is_admin(self) -> bool:
        """
        Перевіряє чи користувач є адміністратором.
        
        Returns:
            bool: True якщо користувач має роль ADMIN, False інакше
            
        Example:
            >>> admin_user = User(role=UserRole.ADMIN)
            >>> admin_user.is_admin()
            True
            >>> regular_user = User(role=UserRole.USER)
            >>> regular_user.is_admin()
            False
        """
        return self.role == UserRole.ADMIN
    
    def __repr__(self) -> str:
        """
        Строкове представлення користувача для відладки.
        
        Returns:
            str: Строкове представлення об'єкта
            
        Example:
            >>> user = User(id=1, username='john', email='john@example.com')
            >>> repr(user)
            "<User(id=1, username='john', email='john@example.com')>"
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """
        Конвертує об'єкт користувача в словник (без конфіденційних даних).
        
        Returns:
            dict: Словник з публічними даними користувача
            
        Note:
            Не включає хешований пароль та токени безпеки
            
        Example:
            >>> user = User(id=1, username='john', email='john@example.com')
            >>> user_dict = user.to_dict()
            >>> 'hashed_password' in user_dict
            False
            >>> user_dict['username']
            'john'
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'role': self.role.value if self.role else None,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }