from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.user import UserRole


class UserCreate(BaseModel):
    telegram_id: int
    full_name: str
    phone: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    role: UserRole


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    telegram_id: int
    full_name: str
    phone: Optional[str]
    login: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
