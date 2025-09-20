from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.api.v1.api import api_router
from app.database.base import Base
from app.database.connection import engine
from app.middleware.rate_limiter import limiter

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="REST API for contacts management with JWT authentication",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Підключення роутерів
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    """Головна сторінка API"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users", 
            "contacts": "/api/v1/contacts"
        }
    }

@app.get("/health")
def health_check():
    """Перевірка здоров'я API"""
    return {"status": "healthy", "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)