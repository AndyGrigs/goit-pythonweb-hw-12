import cloudinary
import cloudinary.uploader
from app.config import settings

# Ініціалізація Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)

def upload_avatar(file_content: bytes, filename: str) -> str:
    """Завантаження аватара в Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            file_content,
            public_id=f"avatars/{filename}",
            transformation=[
                {'width': 300, 'height': 300, 'crop': 'fill'},
                {'quality': 'auto'},
                {'format': 'jpg'}
            ]
        )
        return result['secure_url']
    except Exception as e:
        raise Exception(f"Failed to upload avatar: {str(e)}")

def delete_avatar(public_id: str):
    """Видалення аватара з Cloudinary"""
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass  # Ignore errors when deleting old avatar