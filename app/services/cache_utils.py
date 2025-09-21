import logging
from app.services.redis import redis_service

logger = logging.getLogger(__name__)

def invalidate_user_cache(user_email: str):
    """Функція для інвалідації кешу користувача"""
    redis_service.delete_user_cache(user_email)
    logger.debug(f"Cache invalidated for user {user_email}")