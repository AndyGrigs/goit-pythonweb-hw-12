from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.config import settings

limiter = Limiter(key_func=get_remote_address)

def get_rate_limit_for_me():
    """Rate limit для /me ендпоінту"""
    return f"{settings.rate_limit_me_endpoint}/minute"