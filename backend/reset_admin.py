"""
Admin parolini reset qilish skripti.
Ishlatish: python reset_admin.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.config import settings

def reset_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.login == settings.FIRST_ADMIN_LOGIN).first()
        if user:
            user.hashed_password = hash_password(settings.FIRST_ADMIN_PASSWORD)
            user.is_active = True
            db.commit()
            print(f"✓ Admin paroli yangilandi")
            print(f"  Login   : {settings.FIRST_ADMIN_LOGIN}")
            print(f"  Parol   : {settings.FIRST_ADMIN_PASSWORD}")
        else:
            user = User(
                telegram_id=0,
                full_name="Administrator",
                login=settings.FIRST_ADMIN_LOGIN,
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(user)
            db.commit()
            print(f"✓ Admin yaratildi")
            print(f"  Login   : {settings.FIRST_ADMIN_LOGIN}")
            print(f"  Parol   : {settings.FIRST_ADMIN_PASSWORD}")
    except Exception as e:
        db.rollback()
        print(f"✗ Xatolik: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
