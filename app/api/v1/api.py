from fastapi import APIRouter
from app.api.v1.endpoints import contacts, auth, users

api_router = APIRouter()

# Підключення всіх роутерів
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])