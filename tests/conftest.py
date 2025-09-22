import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from unittest.mock import Mock

from app.main import app
from app.database.base import Base
from app.database.connection import get_db
from app.models.users import User, UserRole
from app.models.contacts import Contact
from app.utils.auth import get_password_hash, create_access_token
from app.services.redis import redis_service
from app.services.email import send_verification_email, send_password_reset_email
from app.services.cloudinary import upload_avatar
from datetime import timedelta

# Налаштування тестової бази даних
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Створює event loop для всієї сесії тестування"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Створює тестову базу даних для кожного тесту"""
    # Створюємо таблиці
    Base.metadata.create_all(bind=engine)
    
    # Створюємо сесію
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Очищаємо таблиці після тесту
        Base.metadata.drop_all(bind=engine)

def override_get_db(db_session):
    """Перевизначаємо залежність бази даних"""
    def _override():
        try:
            yield db_session
        finally:
            pass
    return _override

@pytest.fixture
def client(db_session):
    """Створює тестовий клієнт FastAPI"""
    app.dependency_overrides[get_db] = override_get_db(db_session)
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Тестові дані користувача"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": UserRole.USER
    }

@pytest.fixture
def test_admin_data():
    """Тестові дані адміністратора"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": UserRole.ADMIN
    }

@pytest.fixture
def test_contact_data():
    """Тестові дані контакту"""
    return {
        "first_name": "Іван",
        "last_name": "Петренко", 
        "email": "ivan@example.com",
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Тестовий контакт"
    }

@pytest.fixture
def create_test_user(db_session, test_user_data):
    """Створює тестового користувача в базі"""
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        role=test_user_data["role"],
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def create_test_admin(db_session, test_admin_data):
    """Створює тестового адміністратора в базі"""
    admin = User(
        username=test_admin_data["username"],
        email=test_admin_data["email"],
        hashed_password=get_password_hash(test_admin_data["password"]),
        role=test_admin_data["role"],
        is_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def create_test_contact(db_session, create_test_user, test_contact_data):
    """Створює тестовий контакт в базі"""
    contact = Contact(
        first_name=test_contact_data["first_name"],
        last_name=test_contact_data["last_name"],
        email=test_contact_data["email"],
        phone_number=test_contact_data["phone_number"],
        birth_date=test_contact_data["birth_date"],
        additional_data=test_contact_data["additional_data"],
        owner_id=create_test_user.id
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact

@pytest.fixture
def user_token(create_test_user):
    """Створює JWT токен для тестового користувача"""
    access_token_expires = timedelta(minutes=30)
    return create_access_token(
        data={"sub": create_test_user.email, "role": create_test_user.role.value},
        expires_delta=access_token_expires
    )

@pytest.fixture
def admin_token(create_test_admin):
    """Створює JWT токен для тестового адміністратора"""
    access_token_expires = timedelta(minutes=30)
    return create_access_token(
        data={"sub": create_test_admin.email, "role": create_test_admin.role.value},
        expires_delta=access_token_expires
    )

@pytest.fixture
def auth_headers(user_token):
    """Створює заголовки авторизації для користувача"""
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_headers(admin_token):
    """Створює заголовки авторизації для адміністратора"""
    return {"Authorization": f"Bearer {admin_token}"}

# Мокування зовнішніх сервісів
@pytest.fixture
def mock_redis_service(monkeypatch):
    """Мокує Redis сервіс"""
    mock_redis = Mock()
    mock_redis.is_connected.return_value = True
    mock_redis.get_user_cache.return_value = None
    mock_redis.set_user_cache.return_value = True
    mock_redis.delete_user_cache.return_value = True
    mock_redis.clear_all_cache.return_value = True
    
    monkeypatch.setattr("app.services.redis.redis_service", mock_redis)
    monkeypatch.setattr("app.middleware.auth.redis_service", mock_redis)
    return mock_redis

@pytest.fixture
def mock_email_service(monkeypatch):
    """Мокує email сервіс"""
    async def mock_send_verification_email(email: str, token: str):
        return True
    
    async def mock_send_password_reset_email(email: str, token: str):
        return True
    
    monkeypatch.setattr("app.services.email.send_verification_email", mock_send_verification_email)
    monkeypatch.setattr("app.services.email.send_password_reset_email", mock_send_password_reset_email)

@pytest.fixture
def mock_cloudinary_service(monkeypatch):
    """Мокує Cloudinary сервіс"""
    def mock_upload_avatar(file_content: bytes, filename: str) -> str:
        return f"https://test-cloudinary.com/avatars/{filename}"
    
    monkeypatch.setattr("app.services.cloudinary.upload_avatar", mock_upload_avatar)

@pytest.fixture
def mock_all_external_services(mock_redis_service, mock_email_service, mock_cloudinary_service):
    """Мокує всі зовнішні сервіси разом"""
    pass

# Клас для створення тестових даних
class TestDataFactory:
    @staticmethod
    def create_user_data(**kwargs):
        """Створює тестові дані користувача"""
        default_data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpassword123",
            "role": UserRole.USER
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_contact_data(**kwargs):
        """Створює тестові дані контакту"""
        default_data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "email": "ivan@example.com",
            "phone_number": "+380501234567",
            "birth_date": "1990-05-15",
            "additional_data": "Тестовий контакт"
        }
        default_data.update(kwargs)
        return default_data

@pytest.fixture
def test_data_factory():
    """Надає доступ до фабрики тестових даних"""
    return TestDataFactory