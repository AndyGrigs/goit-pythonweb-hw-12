import redis
import json
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Підключення до Redis"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Перевірка з'єднання
            self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Перевірка чи підключений Redis"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set_user_cache(self, user_email: str, user_data: dict, expire_minutes: Optional[int] = None) -> bool:
        """Кешування даних користувача"""
        if not self.is_connected():
            return False
        
        try:
            key = f"user:{user_email}"
            value = json.dumps(user_data, default=str)
            expire_time = expire_minutes or settings.cache_expire_minutes
            
            self.redis_client.setex(
                name=key,
                time=expire_time * 60,  # конвертуємо в секунди
                value=value
            )
            logger.debug(f"User {user_email} cached for {expire_time} minutes")
            return True
        except Exception as e:
            logger.error(f"Failed to cache user {user_email}: {e}")
            return False
    
    def get_user_cache(self, user_email: str) -> Optional[dict]:
        """Отримання користувача з кешу"""
        if not self.is_connected():
            return None
        
        try:
            key = f"user:{user_email}"
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                user_data = json.loads(cached_data)
                logger.debug(f"User {user_email} found in cache")
                return user_data
            
            logger.debug(f"User {user_email} not found in cache")
            return None
        except Exception as e:
            logger.error(f"Failed to get user {user_email} from cache: {e}")
            return None
    
    def delete_user_cache(self, user_email: str) -> bool:
        """Видалення користувача з кешу"""
        if not self.is_connected():
            return False
        
        try:
            key = f"user:{user_email}"
            result = self.redis_client.delete(key)
            logger.debug(f"User {user_email} cache deleted")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete user {user_email} from cache: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """Очистка всього кешу (для розробки)"""
        if not self.is_connected():
            return False
        
        try:
            self.redis_client.flushdb()
            logger.info("All cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

# Створюємо глобальний екземпляр
redis_service = RedisService()