"""
Database connection setup for Contact Management API

Provides database session management and dependency injection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings


# Database Engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug  # SQL logging in debug mode
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine
)


def get_db():
    """
    Dependency für FastAPI - stellt DB Session bereit
    
    Wird als Dependency in FastAPI Routen verwendet:
    @app.get("/users/")
    def get_users(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Direkte DB Session für manuellen Gebrauch
    WICHTIG: Session muss manuell geschlossen werden!
    
    Beispiel:
    db = get_db_session()
    try:
        # Database operations
        ...
    finally:
        db.close()
    """
    return SessionLocal()


def create_tables():
    """
    Erstellt alle Tabellen basierend auf SQLAlchemy Models
    Nur für Entwicklung/Tests - in Produktion sollten Alembic Migrations verwendet werden
    """
    from app.database.base import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Löscht alle Tabellen - NUR FÜR TESTS!
    """
    from app.database.base import Base
    Base.metadata.drop_all(bind=engine)