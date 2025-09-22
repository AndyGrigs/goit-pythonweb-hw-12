import pytest
from unittest.mock import Mock, patch, AsyncMock
import io

from app.services.redis import RedisService
from app.services.cloudinary import upload_avatar, delete_avatar


@pytest.mark.unit
class TestRedisService:
    """Тести для Redis сервісу"""
    
    @patch('app.services.redis.redis')
    def test_redis_service_connect_success(self, mock_redis):
        """Тест успішного підключення до Redis"""
        mock_redis_client = Mock()
        mock_redis.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        
        service = RedisService()
        
        assert service.redis_client == mock_redis_client
        mock_redis_client.ping.assert_called_once()
    
    @patch('app.services.redis.redis')
    def test_redis_service_connect_failure(self, mock_redis):
        """Тест невдалого підключення до Redis"""
        mock_redis.Redis.side_effect = Exception("Connection failed")
        
        service = RedisService()
        
        assert service.redis_client is None
    
    def test_is_connected_true(self):
        """Тест перевірки з'єднання (підключений)"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        
        assert service.is_connected() is True
        service.redis_client.ping.assert_called_once()
    
    def test_is_connected_false_no_client(self):
        """Тест перевірки з'єднання (немає клієнта)"""
        service = RedisService()
        service.redis_client = None
        
        assert service.is_connected() is False
    
    def test_is_connected_false_ping_fails(self):
        """Тест перевірки з'єднання (ping не працює)"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.side_effect = Exception("Ping failed")
        
        assert service.is_connected() is False
    
    def test_set_user_cache_success(self):
        """Тест успішного кешування користувача"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.setex.return_value = True
        
        user_data = {"id": 1, "email": "test@example.com"}
        
        result = service.set_user_cache("test@example.com", user_data, 15)
        
        assert result is True
        service.redis_client.setex.assert_called_once()
    
    def test_set_user_cache_not_connected(self):
        """Тест кешування коли Redis не підключений"""
        service = RedisService()
        service.redis_client = None
        
        user_data = {"id": 1, "email": "test@example.com"}
        
        result = service.set_user_cache("test@example.com", user_data)
        
        assert result is False
    
    def test_set_user_cache_exception(self):
        """Тест кешування з винятком"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.setex.side_effect = Exception("Redis error")
        
        user_data = {"id": 1, "email": "test@example.com"}
        
        result = service.set_user_cache("test@example.com", user_data)
        
        assert result is False
    
    def test_get_user_cache_success(self):
        """Тест успішного отримання з кешу"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.get.return_value = '{"id": 1, "email": "test@example.com"}'
        
        result = service.get_user_cache("test@example.com")
        
        assert result == {"id": 1, "email": "test@example.com"}
        service.redis_client.get.assert_called_once_with("user:test@example.com")
    
    def test_get_user_cache_not_found(self):
        """Тест отримання з кешу (не знайдено)"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.get.return_value = None
        
        result = service.get_user_cache("test@example.com")
        
        assert result is None
    
    def test_get_user_cache_not_connected(self):
        """Тест отримання з кешу коли Redis не підключений"""
        service = RedisService()
        service.redis_client = None
        
        result = service.get_user_cache("test@example.com")
        
        assert result is None
    
    def test_delete_user_cache_success(self):
        """Тест успішного видалення з кешу"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.delete.return_value = 1
        
        result = service.delete_user_cache("test@example.com")
        
        assert result is True
        service.redis_client.delete.assert_called_once_with("user:test@example.com")
    
    def test_delete_user_cache_not_found(self):
        """Тест видалення з кешу (не знайдено)"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.delete.return_value = 0
        
        result = service.delete_user_cache("test@example.com")
        
        assert result is False
    
    def test_clear_all_cache_success(self):
        """Тест очистки всього кешу"""
        service = RedisService()
        service.redis_client = Mock()
        service.redis_client.ping.return_value = True
        service.redis_client.flushdb.return_value = True
        
        result = service.clear_all_cache()
        
        assert result is True
        service.redis_client.flushdb.assert_called_once()
    
    def test_clear_all_cache_not_connected(self):
        """Тест очистки кешу коли Redis не підключений"""
        service = RedisService()
        service.redis_client = None
        
        result = service.clear_all_cache()
        
        assert result is False


@pytest.mark.unit
class TestCloudinaryService:
    """Тести для Cloudinary сервісу"""
    
    @patch('app.services.cloudinary.cloudinary.uploader.upload')
    def test_upload_avatar_success(self, mock_upload):
        """Тест успішного завантаження аватара"""
        mock_upload.return_value = {
            'secure_url': 'https://cloudinary.com/avatars/test.jpg'
        }
        
        file_content = b"fake image content"
        filename = "test_avatar.jpg"
        
        result = upload_avatar(file_content, filename)
        
        assert result == 'https://cloudinary.com/avatars/test.jpg'
        mock_upload.assert_called_once_with(
            file_content,
            public_id=f"avatars/{filename}",
            transformation=[
                {'width': 300, 'height': 300, 'crop': 'fill'},
                {'quality': 'auto'},
                {'format': 'jpg'}
            ]
        )
    
    @patch('app.services.cloudinary.cloudinary.uploader.upload')
    def test_upload_avatar_failure(self, mock_upload):
        """Тест невдалого завантаження аватара"""
        mock_upload.side_effect = Exception("Cloudinary error")
        
        file_content = b"fake image content"
        filename = "test_avatar.jpg"
        
        with pytest.raises(Exception) as exc_info:
            upload_avatar(file_content, filename)
        
        assert "Failed to upload avatar" in str(exc_info.value)
    
    @patch('app.services.cloudinary.cloudinary.uploader.destroy')
    def test_delete_avatar_success(self, mock_destroy):
        """Тест успішного видалення аватара"""
        mock_destroy.return_value = True
        
        delete_avatar("avatars/test_avatar")
        
        mock_destroy.assert_called_once_with("avatars/test_avatar")
    
    @patch('app.services.cloudinary.cloudinary.uploader.destroy')
    def test_delete_avatar_failure(self, mock_destroy):
        """Тест що помилки при видаленні ігноруються"""
        mock_destroy.side_effect = Exception("Cloudinary error")
        
        # Не повинно викидати виняток
        delete_avatar("avatars/test_avatar")
        
        mock_destroy.assert_called_once_with("avatars/test_avatar")


@pytest.mark.unit
@pytest.mark.asyncio
class TestEmailService:
    """Тести для Email сервісу"""
    
    @patch('app.services.email.FastMail')
    async def test_send_verification_email_success(self, mock_fastmail_class):
        """Тест успішної відправки verification email"""
        mock_fastmail = Mock()
        mock_fastmail_class.return_value = mock_fastmail
        mock_fastmail.send_message = AsyncMock()
        
        from app.services.email import send_verification_email
        
        await send_verification_email("test@example.com", "test_token_123")
        
        mock_fastmail.send_message.assert_called_once()
        # Перевіряємо, що аргумент містить правильні дані
        call_args = mock_fastmail.send_message.call_args[0][0]
        assert call_args.subject == "Verify your email - Contact Management API"
        assert "test@example.com" in call_args.recipients
        assert "test_token_123" in call_args.body
    
    @patch('app.services.email.FastMail')
    async def test_send_password_reset_email_success(self, mock_fastmail_class):
        """Тест успішної відправки password reset email"""
        mock_fastmail = Mock()
        mock_fastmail_class.return_value = mock_fastmail
        mock_fastmail.send_message = AsyncMock()
        
        from app.services.email import send_password_reset_email
        
        await send_password_reset_email("test@example.com", "reset_token_123")
        
        mock_fastmail.send_message.assert_called_once()
        call_args = mock_fastmail.send_message.call_args[0][0]
        assert call_args.subject == "Password Reset - Contact Management API"
        assert "test@example.com" in call_args.recipients
        assert "reset_token_123" in call_args.body
    
    @patch('app.services.email.FastMail')
    async def test_send_verification_email_failure(self, mock_fastmail_class):
        """Тест невдалої відправки verification email"""
        mock_fastmail = Mock()
        mock_fastmail_class.return_value = mock_fastmail
        mock_fastmail.send_message = AsyncMock(side_effect=Exception("SMTP error"))
        
        from app.services.email import send_verification_email
        
        # Email service повинен викидати виняток при помилці
        with pytest.raises(Exception):
            await send_verification_email("test@example.com", "test_token_123")
    
    @patch('app.services.email.FastMail')
    async def test_send_password_reset_email_failure(self, mock_fastmail_class):
        """Тест невдалої відправки password reset email"""
        mock_fastmail = Mock()
        mock_fastmail_class.return_value = mock_fastmail
        mock_fastmail.send_message = AsyncMock(side_effect=Exception("SMTP error"))
        
        from app.services.email import send_password_reset_email
        
        with pytest.raises(Exception):
            await send_password_reset_email("test@example.com", "reset_token_123")


@pytest.mark.unit
class TestCacheUtils:
    """Тести для cache utils"""
    
    @patch('app.services.cache_utils.redis_service')
    def test_invalidate_user_cache(self, mock_redis_service):
        """Тест інвалідації кешу користувача"""
        from app.services.cache_utils import invalidate_user_cache
        
        mock_redis_service.delete_user_cache.return_value = True
        
        invalidate_user_cache("test@example.com")
        
        mock_redis_service.delete_user_cache.assert_called_once_with("test@example.com")