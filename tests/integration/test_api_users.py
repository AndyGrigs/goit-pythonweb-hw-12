import pytest
from fastapi import status
from unittest.mock import Mock
import io


@pytest.mark.integration
@pytest.mark.api
class TestUsersAPI:
    """Інтеграційні тести для API користувачів"""
    
    def test_get_current_user_success(self, client, auth_headers, create_test_user, mock_all_external_services):
        """Тест отримання поточного користувача з валідним токеном"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == create_test_user.id
        assert data["username"] == create_test_user.username
        assert data["email"] == create_test_user.email
        assert data["role"] == create_test_user.role.value
        assert data["is_verified"] == create_test_user.is_verified
        assert "hashed_password" not in data
    
    def test_get_current_user_no_token(self, client, mock_all_external_services):
        """Тест отримання поточного користувача без токена"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_current_user_invalid_token(self, client, mock_all_external_services):
        """Тест отримання поточного користувача з невалідним токеном"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_unverified(self, client, db_session, mock_all_external_services):
        """Тест отримання поточного користувача неверифікованим користувачем"""
        from app.models.users import User, UserRole
        from app.utils.auth import get_password_hash, create_access_token
        from datetime import timedelta
        
        # Створюємо неверифікованого користувача
        unverified_user = User(
            username="unverified",
            email="unverified@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_verified=False
        )
        db_session.add(unverified_user)
        db_session.commit()
        db_session.refresh(unverified_user)
        
        # Створюємо токен для неверифікованого користувача
        token = create_access_token(
            data={"sub": unverified_user.email, "role": unverified_user.role.value},
            expires_delta=timedelta(minutes=30)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/users/me", headers=headers)
        
        # Доступ до /me має бути заборонений для неверифікованих користувачів
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not verified" in response.json()["detail"]
    
    def test_upload_avatar_success_admin(self, client, admin_headers, create_test_admin, mock_all_external_services):
        """Тест успішного завантаження аватара адміністратором"""
        # Створюємо фіктивний файл зображення
        file_content = b"fake image content"
        files = {
            "file": ("avatar.jpg", io.BytesIO(file_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "avatar_url" in data
        assert data["avatar_url"] is not None
        assert "cloudinary" in data["avatar_url"]  # Мокований URL
    
    def test_upload_avatar_forbidden_user(self, client, auth_headers, mock_all_external_services):
        """Тест що звичайний користувач не може завантажувати аватар"""
        file_content = b"fake image content"
        files = {
            "file": ("avatar.jpg", io.BytesIO(file_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]
    
    def test_upload_avatar_invalid_file_type(self, client, admin_headers, mock_all_external_services):
        """Тест завантаження файлу неправильного типу"""
        file_content = b"not an image"
        files = {
            "file": ("document.txt", io.BytesIO(file_content), "text/plain")
        }
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be an image" in response.json()["detail"]
    
    def test_upload_avatar_file_too_large(self, client, admin_headers, mock_all_external_services):
        """Тест завантаження занадто великого файлу"""
        # Створюємо файл більше 5MB
        large_file_content = b"x" * (6 * 1024 * 1024)  # 6MB
        files = {
            "file": ("large_avatar.jpg", io.BytesIO(large_file_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "too large" in response.json()["detail"]
    
    def test_upload_avatar_no_file(self, client, admin_headers, mock_all_external_services):
        """Тест завантаження без файлу"""
        response = client.post("/api/v1/users/me/avatar", headers=admin_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_user_role_success_admin(self, client, admin_headers, create_test_user, mock_all_external_services):
        """Тест успішної зміни ролі користувача адміністратором"""
        role_data = {"role": "admin"}
        
        response = client.patch(f"/api/v1/users/{create_test_user.id}/role", json=role_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "admin"
        assert data["id"] == create_test_user.id
    
    def test_update_user_role_forbidden_user(self, client, auth_headers, create_test_user, mock_all_external_services):
        """Тест що звичайний користувач не може змінювати ролі"""
        role_data = {"role": "admin"}
        
        response = client.patch(f"/api/v1/users/{create_test_user.id}/role", json=role_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]
    
    def test_update_user_role_admin_demoting_self(self, client, admin_headers, create_test_admin, mock_all_external_services):
        """Тест що адмін не може понизити сам себе"""
        role_data = {"role": "user"}
        
        response = client.patch(f"/api/v1/users/{create_test_admin.id}/role", json=role_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot demote themselves" in response.json()["detail"]
    
    def test_update_user_role_nonexistent_user(self, client, admin_headers, mock_all_external_services):
        """Тест зміни ролі неіснуючого користувача"""
        role_data = {"role": "admin"}
        
        response = client.patch("/api/v1/users/99999/role", json=role_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_update_user_role_invalid_role(self, client, admin_headers, create_test_user, mock_all_external_services):
        """Тест зміни ролі на невалідну"""
        role_data = {"role": "invalid_role"}
        
        response = client.patch(f"/api/v1/users/{create_test_user.id}/role", json=role_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
@pytest.mark.api
class TestUsersAPIRateLimit:
    """Тести для rate limiting на /me ендпоінті"""
    
    def test_rate_limit_me_endpoint(self, client, auth_headers, mock_all_external_services):
        """Тест rate limiting на /me ендпоінті"""
        # Налаштування rate limit в settings = 10 запитів на хвилину
        
        # Робимо 10 запитів (має працювати)
        for i in range(10):
            response = client.get("/api/v1/users/me", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
        
        # 11-й запит має бути заблокований
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.integration
@pytest.mark.api
class TestUsersAPIFlow:
    """Тести для комплексних scenarios з користувачами"""
    
    def test_user_promotion_flow(self, client, create_test_user, create_test_admin, mock_all_external_services):
        """Тест повного циклу підвищення користувача до адміністратора"""
        from app.utils.auth import create_access_token
        from datetime import timedelta
        
        # 1. Звичайний користувач намагається завантажити аватар (має бути заборонено)
        user_token = create_access_token(
            data={"sub": create_test_user.email, "role": create_test_user.role.value},
            expires_delta=timedelta(minutes=30)
        )
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        file_content = b"fake image"
        files = {"file": ("avatar.jpg", io.BytesIO(file_content), "image/jpeg")}
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=user_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # 2. Адмін підвищує користувача до адміністратора
        admin_token = create_access_token(
            data={"sub": create_test_admin.email, "role": create_test_admin.role.value},
            expires_delta=timedelta(minutes=30)
        )
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        role_data = {"role": "admin"}
        response = client.patch(f"/api/v1/users/{create_test_user.id}/role", json=role_data, headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Тепер користувач має нові права (створюємо новий токен з новою роллю)
        new_user_token = create_access_token(
            data={"sub": create_test_user.email, "role": "admin"},
            expires_delta=timedelta(minutes=30)
        )
        new_user_headers = {"Authorization": f"Bearer {new_user_token}"}
        
        # 4. Тепер користувач може завантажувати аватар
        response = client.post("/api/v1/users/me/avatar", files=files, headers=new_user_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_avatar_upload_and_profile_update_flow(self, client, create_test_admin, mock_all_external_services):
        """Тест завантаження аватара та оновлення профілю"""
        from app.utils.auth import create_access_token
        from datetime import timedelta
        
        admin_token = create_access_token(
            data={"sub": create_test_admin.email, "role": create_test_admin.role.value},
            expires_delta=timedelta(minutes=30)
        )
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. Перевіряємо початковий стан профілю
        response = client.get("/api/v1/users/me", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        initial_data = response.json()
        assert initial_data["avatar_url"] is None
        
        # 2. Завантажуємо аватар
        file_content = b"fake avatar image"
        files = {"file": ("new_avatar.jpg", io.BytesIO(file_content), "image/jpeg")}
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        upload_data = response.json()
        assert upload_data["avatar_url"] is not None
        assert "cloudinary" in upload_data["avatar_url"]
        
        # 3. Перевіряємо, що аватар оновився в профілі
        response = client.get("/api/v1/users/me", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        final_data = response.json()
        assert final_data["avatar_url"] == upload_data["avatar_url"]