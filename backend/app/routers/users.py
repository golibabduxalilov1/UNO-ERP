from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.core.deps import require_roles, get_current_user, verify_internal_key
from app.core.security import hash_password
from app.services.audit_service import log_action

router = APIRouter(prefix="/users", tags=["users"])

ADMIN_ROLES = [UserRole.admin]


@router.get("", response_model=List[UserOut])
def list_users(
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    return q.order_by(User.full_name).all()


@router.post("", response_model=UserOut)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    existing = db.query(User).filter(User.telegram_id == data.telegram_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu Telegram ID allaqachon ro'yxatdan o'tgan")
    if data.login:
        login_exists = db.query(User).filter(User.login == data.login).first()
        if login_exists:
            raise HTTPException(status_code=400, detail="Bu login allaqachon mavjud")
    user = User(
        telegram_id=data.telegram_id,
        full_name=data.full_name,
        phone=data.phone,
        login=data.login,
        hashed_password=hash_password(data.password) if data.password else None,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, "create_user", user_id=current_user.id, entity_type="user", entity_id=user.id, details=f"Yaratildi: {user.full_name}")
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(ADMIN_ROLES)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    first_admin = db.query(User).filter(User.role == UserRole.admin).order_by(User.id).first()
    if first_admin and user.id == first_admin.id and data.role is not None and data.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Birinchi administrator roli o'zgartirib bo'lmaydi")
    if user.role == UserRole.admin and user.id != current_user.id:
        if not first_admin or current_user.id != first_admin.id:
            raise HTTPException(status_code=403, detail="Faqat birinchi administrator boshqa adminlarni o'zgartira oladi")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.phone is not None:
        user.phone = data.phone
    if data.login is not None:
        user.login = data.login
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    log_action(db, "update_user", user_id=current_user.id, entity_type="user", entity_id=user.id)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.admin])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
    if user.role == UserRole.admin:
        first_admin = db.query(User).filter(User.role == UserRole.admin).order_by(User.id).first()
        if not first_admin or current_user.id != first_admin.id:
            raise HTTPException(status_code=403, detail="Faqat birinchi administrator boshqa adminlarni o'chira oladi")

    db.delete(user)
    db.commit()
    log_action(db, "delete_user", user_id=current_user.id, entity_type="user", entity_id=user_id)
    return {"message": "Foydalanuvchi o'chirildi"}


@router.get("/by-telegram/{telegram_id}", response_model=UserOut)
def get_by_telegram(
    telegram_id: int,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = db.query(User).filter(User.telegram_id == telegram_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user
