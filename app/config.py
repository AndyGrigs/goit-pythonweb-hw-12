from pydantic_settings import BaseSettings 
from typing import Optional

class Settings(BaseSettings):
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "contacts_db"
    db_user: str = "contacts_user"
    db_password: str = "contacts_password"
    
    # Application
    app_name: str = "Contact Management API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security (додаємо нові поля)
    secret_key: str = "your-super-secret-jwt-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email Configuration (додаємо нові поля)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    
    # Cloudinary (додаємо нові поля)
    cloudinary_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    # Rate Limiting (додаємо нове поле)
    rate_limit_me_endpoint: int = 10
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()